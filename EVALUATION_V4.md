# Message Check — prompt v4 evaluation

Reviewed October 31, 2026.

**Decision: retain `automated-prompt-v4` as the current development version.**
It improves assessment agreement on the original set, preserves every
previously matching assessment across the two sets, and produces exact
message-only evidence in these runs. Explanation quality remains uneven:
there are unsupported labels, overstated verification, and an example that
changes who performs an action. This is a development checkpoint, not a
claim of deployment readiness or established real-world accuracy.

## Comparison with v2

| Dataset | v2 agreement | v4 agreement | Change |
| --- | --- | --- | --- |
| `data/test_cases.json` | 17/20 (85.0%) | 19/20 (95.0%) | Two additional matches |
| `data/validation_cases.json` | 16/18 (88.9%) | 16/18 (88.9%) | Same assessment for every case |
| Combined | 33/38 (86.8%) | 35/38 (92.1%) | Two additional matches; no new assessment mismatches |

Both dataset byte hashes match the earlier v2 reports. Case IDs, messages,
contexts, and reference answers also match. The recorded model tag and
generation settings are unchanged. These are comparisons of observed runs;
the reports do not establish an identical model digest or runtime environment.

The two changed assessments are:

| Case | Situation | v2 | v4 / reference |
| --- | --- | --- | --- |
| `case_006` | A user-requested reset code, with an instruction not to share it | `concerning` | `no_clear_concern` |
| `case_009` | A booking deposit with incomplete provider and payment context | `concerning` | `insufficient_context` |

Across v4's 38 answers, all 14 cases labeled `concerning` by the references
were flagged, and all 12 labeled `no_clear_concern` matched. Nine of the 12
`insufficient_context` references matched. These counts are conditional on
the current provisional labels, not independently established ground truth.

## Checks on the saved outputs

- All 38 requests completed; the reports record no request or schema errors.
- All 38 raw JSON responses reproduce their saved `analysis` objects.
- Eighteen responses supplied evidence, containing 25 quoted excerpts in total.
  Every excerpt is an exact substring of its message. The other 20 answers
  have empty evidence arrays.
- All recorded `review_flags` arrays are empty. This does not establish
  correct meaning, relevant evidence, complete concern coverage, or sound reasoning.
- Every response records `done_reason: stop`; none records output truncation.
- Mean elapsed time was 18.0 seconds for the original set and 17.6 seconds
  for the validation set, as recorded on the user's machine. These are not
  controlled performance comparisons with v2.

## Three remaining assessment disagreements

All three were already disagreements in v2.

| Case | Message / situation | Reference | v4 | Interpretation under the current policy |
| --- | --- | --- | --- | --- |
| `case_015` | "Keep this between us. Please don't ask anyone else about it." No context. | `insufficient_context` | `no_clear_concern` | The topic and reason for secrecy could materially change the interpretation. |
| `validation_007` | "Please keep this private until Friday. I don't want anyone else to know yet." No context. | `insufficient_context` | `no_clear_concern` | The policy asks the model to preserve uncertainty about the unspecified subject and purpose. |
| `validation_013` | Upload a government-ID photo to finish registration; service, purpose, and destination unspecified. | `insufficient_context` | `concerning` | Sensitive information warrants caution, but unknown details alone do not establish wrongdoing; registration may involve an ordinary identity check. |

Privacy requests and identity checks involve policy choices. Keep the labels
unchanged for this comparison. Clarify the written rubric before changing
either references or the prompt; changing labels to raise the score would
make this comparison misleading.

## Meaning and explanation review

The account/password example (`case_001`) now identifies the password
request without inventing a future blocking threat. The conditional violence
example (`validation_010`) now correctly says harm is threatened **if the
recipient leaves**. The two prompt-injection examples (`case_020` and
`validation_012`) retain concerning assessments despite instructions embedded
in the analyzed messages. These are successes on these examples only.

Remaining issues include:

| Cases | Observation | Desired behavior |
| --- | --- | --- |
| `validation_001`; related wording in `case_006` and `case_008` | `validation_001` calls the interaction "verified". Other answers use "the context confirms" and language about authenticity or legitimacy. | Attribute information to the supplied context and describe consistency with an ordinary interaction; do not imply independent verification. The explicit "verified interaction" wording is a worsening from the recorded v2 answer. |
| `validation_007`, `validation_010` | The phrase "The context is null" reappears. | Explain the relevant missing background in ordinary language, only when it matters. Its absence in the earlier eight-case run did not generalize. |
| `validation_018` | A label and explanation describe a "demand to cancel a charge". The message actually asks for remote access so **the sender claims they can cancel it**. | Preserve the actor and claimed purpose. Identify the remote-access request and discouragement of independent contact. This cancellation-demand wording is a new error relative to the recorded v2 answer. |
| `case_014` | `instruct_to_stop_contacting_us` misdescribes "Don't call your usual contact". | Identify discouragement of independent verification without changing who the recipient is told not to contact. |
| `case_009` | The assessment improves, but the explanation calls the deposit unusual based on details the analyzer was not given. | Keep missing information distinct from evidence that the provider omitted or concealed it. |
| `case_017` | One exact quote ends mid-word: "purchase $300 in gift card". The answer also mentions "personal verification data", although the requested material is gift-card codes. | Prefer complete, relevant excerpts and the actual requested item. Exact-substring checks cannot establish semantic precision. |
| `validation_017` | The explanation treats uncertainty about the sender's knowledge as support for the threat. | The explicit conditional threat supports concern; uncertainty limits what is known about the sender's ability to carry it out. |
| `case_012`, `validation_015` | Correct insufficient-context labels, but little acknowledgment of wording that links affection or family loyalty to compliance. | Describe the observable emotional pressure while preserving uncertainty about the request and intent. |

`case_019` ("You're dead when I see you 😂") matches its provisional
`insufficient_context` label, but still deserves rubric review: violent wording
should be acknowledged, and the emoji does not establish joking or safety.
The match must not be treated as proof that the explanation is adequate.

The earlier eight-case grounding run was 8/8 on assessments, with remaining
issues in `grounding_002` (threat omitted from concerns/evidence),
`grounding_003` (unsupported `threat_to_disable_profile`), and
`grounding_005` (overstated verification). The present broader evaluation
does not resolve those failures. Keep that run separate from the 38-case
comparison above.

## Configuration and provenance

| Setting | Recorded value |
| --- | --- |
| Model | `qwen3:4b-instruct-2507-q4_K_M` |
| Prompt | `automated-prompt-v4` |
| Validator | `output-checks-v2` |
| Temperature | `0` |
| Context limit | `4096` |
| Output limit | `512` |

Reports used:

- v4 original set: `evaluation_20261031T223054_364237Z.json`
- v4 validation set: `evaluation_20261031T223707_408486Z.json`
- v2 original set: `evaluation_20261017T191607_666348Z.json`
- v2 validation set: `evaluation_20261017T200635_371171Z.json`
- Earlier v4 grounding run: `evaluation_20261031T221854_108707Z.json`

Dataset SHA-256 values:

```text
test_cases.json:
dd7f8280211b72693e8c04a19d94a09a827b0a76aed4e6fb66dac74254e961c1

validation_cases.json:
4565d19c030df09fade445dae2745444a15bc2fd16150d13a54e64c5bfe0997b
```

All these examples are now development data. The 92.1% combined agreement
is not an estimate of real-world accuracy. The review did not change the
prompt, reference labels, validator, or model; it analyzed existing outputs.
It did not run new model inference or establish repeatability across runs.

## Next action

Preserve v4 and this review in Git, leaving `BASELINE.md` as the historical
v0.1.0 record. Run the existing offline tests on the actual laptop files,
then review and commit `evaluate_v2.py`, `data/grounding_cases.json`, and
this document. Keep generated reports in the existing ignored `results`
folder. No repository commit or push is claimed by this review.

For the next model experiment, first clarify uncertainty and verification
rules, then add fresh paired examples covering actor/condition preservation,
privacy requests, and identity-check context. Define expected explanations
before inspecting new outputs. Measure label agreement and explanation
grounding separately; avoid declaring the original issue fixed from one
successful wording.
