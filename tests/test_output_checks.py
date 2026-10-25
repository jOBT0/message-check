"""Offline regression tests for Message Check's output contract.

Run from AI_Project with:
    python -m unittest discover -s tests -p "test_*.py" -v

All HTTP calls are replaced with test doubles. Ollama is not needed.
These tests exercise Python behavior, not the model's judgment of messages.
"""

import copy
import io
import json
import unittest
import urllib.error
from unittest.mock import patch

import evaluate_v2 as engine


PASSWORD_MESSAGE = "Your account is blocked. Reply with your password to restore access."
PASSWORD_QUOTE = "Reply with your password"
MONEY_MESSAGE = "Can you send me the money today?"


def answer(**changes):
    """Return a fresh, synthetic model answer for each test."""
    result = {
        "assessment": "concerning",
        "concerns": ["request_for_password"],
        "evidence": [PASSWORD_QUOTE],
        "explanation": "The message asks the recipient to disclose an account password.",
    }
    result.update(changes)
    return result


def http_reply(raw_content, done_reason="stop"):
    """An in-memory HTTP response with the fields consumed by the engine."""
    body = {
        "model": engine.DEFAULT_MODEL,
        "message": {"role": "assistant", "content": raw_content},
        "done_reason": done_reason,
    }
    return io.BytesIO(json.dumps(body, ensure_ascii=False).encode("utf-8"))


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        # An unexpected HTTP attempt fails immediately instead of contacting Ollama.
        patcher = patch.object(
            engine.urllib.request,
            "urlopen",
            side_effect=AssertionError("Unexpected HTTP request in an offline test."),
        )
        self.http = patcher.start()
        self.addCleanup(patcher.stop)

    def reply_with(self, raw_content, done_reason="stop"):
        self.http.side_effect = None
        self.http.return_value = http_reply(raw_content, done_reason)


class SchemaTests(OfflineTestCase):
    def test_accepts_the_three_supported_assessments(self):
        for assessment in ("concerning", "insufficient_context", "no_clear_concern"):
            with self.subTest(assessment=assessment):
                result = answer(assessment=assessment)
                if assessment != "concerning":
                    result.update(concerns=[], evidence=[])
                self.assertEqual(engine.validate_analysis(result), [])

    def test_rejects_non_object_outputs(self):
        for result in (None, [], "concerning", 42):
            with self.subTest(result=result):
                self.assertTrue(engine.validate_analysis(result))

    def test_requires_exactly_the_four_contract_fields(self):
        for missing in ("assessment", "concerns", "evidence", "explanation"):
            with self.subTest(missing=missing):
                result = answer()
                del result[missing]
                self.assertTrue(engine.validate_analysis(result))
        self.assertTrue(engine.validate_analysis(answer(confidence=0.99)))

    def test_rejects_unknown_assessments(self):
        for assessment in ("safe", "scam", "Concerning", "", None):
            with self.subTest(assessment=assessment):
                self.assertTrue(engine.validate_analysis(answer(assessment=assessment)))

    def test_rejects_invalid_array_items_and_explanations(self):
        for field in ("concerns", "evidence"):
            for value in (None, "a string", [""], [" \n"], [1], ["valid text", None]):
                with self.subTest(field=field, value=value):
                    self.assertTrue(engine.validate_analysis(answer(**{field: value})))
        for value in (None, "", " \n", [], 42):
            with self.subTest(explanation=value):
                self.assertTrue(engine.validate_analysis(answer(explanation=value)))


class ReviewTests(OfflineTestCase):
    def review(self, result, message=PASSWORD_MESSAGE, done_reason=None):
        # Review flags must report problems without silently editing the answer.
        original = copy.deepcopy(result)
        self.assertEqual(engine.validate_analysis(result), [])
        flags = engine.review_analysis(result, message, done_reason)
        self.assertEqual(result, original)
        return flags

    def test_accepts_consistent_answers_and_exact_unicode_quotes(self):
        cases = [
            (PASSWORD_MESSAGE, answer()),
            (MONEY_MESSAGE, answer(
                assessment="insufficient_context", concerns=[], evidence=[],
                explanation="The purpose of the payment and relationship are unknown.",
            )),
            ("See you at lunch!", answer(
                assessment="no_clear_concern", concerns=[], evidence=[],
                explanation="This is an ordinary invitation with no clear warning sign.",
            )),
            ("Envoie-moi ton mot de passe.\nGarde ça secret.", answer(
                evidence=["mot de passe.\nGarde ça secret."],
            )),
        ]
        for message, result in cases:
            with self.subTest(message=message):
                self.assertEqual(self.review(result, message), [])

    def test_flags_evidence_without_concerns_for_every_assessment(self):
        # Regression: the user's money-request response had a quote but no concerns.
        for assessment in ("insufficient_context", "no_clear_concern", "concerning"):
            with self.subTest(assessment=assessment):
                result = answer(
                    assessment=assessment, concerns=[], evidence=[MONEY_MESSAGE],
                    explanation="The payment purpose and relationship are unknown.",
                )
                self.assertIn(
                    "Quoted evidence is present, but no concerns are listed.",
                    self.review(result, MONEY_MESSAGE),
                )

    def test_flags_concerning_without_a_listed_concern(self):
        self.assertEqual(
            self.review(answer(concerns=[], evidence=[])),
            ["Concerning assessment has no listed concern."],
        )

    def test_flags_concerns_without_evidence(self):
        self.assertEqual(
            self.review(answer(evidence=[])),
            ["Listed concerns have no quoted evidence."],
        )

    def test_flags_no_clear_concern_with_concern_labels(self):
        self.assertEqual(
            self.review(answer(assessment="no_clear_concern")),
            ["No-clear-concern result has nonempty concern/evidence arrays."],
        )

    def test_flags_paraphrases_and_text_absent_from_the_message(self):
        for quote in (
            "Send us your password",  # Paraphrase, not an exact quote.
            "reply with your password",  # Case differs from the source.
            "An unexpected support message.",  # Context is not message evidence.
        ):
            with self.subTest(quote=quote):
                self.assertEqual(
                    self.review(answer(evidence=[quote])),
                    ["Evidence contains text absent from the message."],
                )

    def test_flags_the_token_limit_even_when_the_json_is_valid(self):
        self.assertEqual(
            self.review(answer(), done_reason="length"),
            ["Generation reached its token limit; inspect completeness."],
        )


class PipelineTests(OfflineTestCase):
    def test_preserves_the_raw_answer_and_its_consistency_warning(self):
        result = answer(
            assessment="insufficient_context", concerns=[], evidence=[MONEY_MESSAGE],
            explanation="The purpose of the payment and relationship are unknown.",
        )
        raw = json.dumps(result, indent=2) + "\n"
        self.reply_with(raw)

        record = engine.analyze_message(MONEY_MESSAGE)

        self.assertIsNone(record["request_error"])
        self.assertEqual(record["validation_errors"], [])
        self.assertEqual(record["raw_response"], raw)
        self.assertEqual(record["analysis"], result)
        self.assertIs(record["evidence_is_exact"], True)
        self.assertEqual(record["review_flags"], [
            "Quoted evidence is present, but no concerns are listed."
        ])

    def test_reports_malformed_json_without_repairing_it(self):
        for raw in ('{"assessment":', '```json\n' + json.dumps(answer()) + '\n```'):
            with self.subTest(raw=raw):
                self.reply_with(raw)
                record = engine.analyze_message(PASSWORD_MESSAGE)
                self.assertIsNone(record["request_error"])
                self.assertEqual(record["raw_response"], raw)
                self.assertIsNone(record["analysis"])
                self.assertTrue(record["validation_errors"])
                self.assertTrue(record["validation_errors"][0].startswith("Invalid JSON:"))
                self.assertIsNone(record["evidence_is_exact"])

    def test_reports_invalid_shape_before_consistency_review(self):
        result = answer(evidence="This should have been an array.")
        self.reply_with(json.dumps(result))

        record = engine.analyze_message(PASSWORD_MESSAGE)

        self.assertEqual(record["analysis"], result)
        self.assertTrue(record["validation_errors"])
        self.assertEqual(record["review_flags"], [])
        self.assertIsNone(record["evidence_is_exact"])

    def test_context_only_quotes_fail_the_message_evidence_check(self):
        context = "An unexpected support message."
        self.reply_with(json.dumps(answer(evidence=[context])))

        record = engine.analyze_message(PASSWORD_MESSAGE, context)

        self.assertEqual(record["validation_errors"], [])
        self.assertIs(record["evidence_is_exact"], False)
        self.assertIn("Evidence contains text absent from the message.", record["review_flags"])

    def test_connection_failure_is_reported_as_an_error_not_an_assessment(self):
        self.http.side_effect = urllib.error.URLError("Simulated connection refusal")

        record = engine.analyze_message(PASSWORD_MESSAGE)

        self.assertTrue(record["request_error"])
        self.assertIsNone(record["analysis"])
        self.assertIsNone(record["raw_response"])
        self.assertEqual(record["validation_errors"], [])

    def test_reference_answers_never_enter_the_model_request(self):
        reference_only = "REFERENCE_ONLY_DO_NOT_SEND_7391"
        case = {
            "id": "synthetic_reference_test",
            "message": PASSWORD_MESSAGE,
            "context": "Someone claims to provide account support.",
            # Deliberately disagree with the simulated answer to exercise scoring.
            "expected": {
                "assessment": "no_clear_concern",
                "explanation": reference_only,
            },
        }
        self.reply_with(json.dumps(answer()))

        record = engine.evaluate_case(case, engine.DEFAULT_MODEL, 17)

        self.http.assert_called_once()
        request = self.http.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/chat")
        self.assertEqual(self.http.call_args.kwargs["timeout"], 17)
        self.assertEqual([m["role"] for m in payload["messages"]], ["system", "user"])
        self.assertEqual(json.loads(payload["messages"][1]["content"]), {
            "message": case["message"], "context": case["context"],
        })
        self.assertNotIn(reference_only, request.data.decode("utf-8"))
        self.assertEqual(record["expected"], case["expected"])
        self.assertIs(record["assessment_matches"], False)

    def test_each_request_has_fresh_message_and_context(self):
        raw = json.dumps(answer())
        self.http.side_effect = [http_reply(raw), http_reply(raw)]
        first_context = "FIRST_CONTEXT_ONLY_5824: an agreed repayment."

        engine.analyze_message(MONEY_MESSAGE, first_context)
        engine.analyze_message(PASSWORD_MESSAGE)

        self.assertEqual(self.http.call_count, 2)
        expected_inputs = [
            {"message": MONEY_MESSAGE, "context": first_context},
            {"message": PASSWORD_MESSAGE, "context": None},
        ]
        for call, expected in zip(self.http.call_args_list, expected_inputs):
            payload = json.loads(call.args[0].data.decode("utf-8"))
            self.assertEqual([m["role"] for m in payload["messages"]], ["system", "user"])
            self.assertEqual(json.loads(payload["messages"][1]["content"]), expected)
        self.assertNotIn(first_context, self.http.call_args_list[1].args[0].data.decode("utf-8"))

    def test_invalid_inputs_are_rejected_before_any_http_request(self):
        invalid_inputs = [
            {"message": ""},
            {"message": " \n"},
            {"message": None},
            {"message": PASSWORD_MESSAGE, "context": 123},
            {"message": PASSWORD_MESSAGE, "model": "example-cloud"},
            {"message": PASSWORD_MESSAGE, "model": ""},
            {"message": PASSWORD_MESSAGE, "timeout": 0},
        ]
        for kwargs in invalid_inputs:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    engine.analyze_message(**kwargs)
        self.http.assert_not_called()


if __name__ == "__main__":
    unittest.main()
