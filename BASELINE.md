# Message Check: baseline record

Recorded October 24, 2026. Suggested Git tag after committing: `v0.1.0`.
This document describes observed behavior. It does not assert that a Git
commit or tag has already been created on the developer's laptop.

## Configuration

| Setting | Value |
| --- | --- |
| Model tag | `qwen3:4b-instruct-2507-q4_K_M` |
| Current prompt version | `automated-prompt-v2` |
| Current validation version | `output-checks-v2` |
| Temperature | `0` |
| Context setting | `num_ctx: 4096` |
| Output limit | `num_predict: 512` |
| Inference endpoint | `http://127.0.0.1:11434/api/chat` |
| Default request timeout | 300 seconds |
| Browser dependency | `gradio==6.30.0` |

The prompt and model-generation settings were preserved when inference was
shared with the CLI and browser interface. The validation revision adds a
warning when evidence is present but concerns are empty. It does not edit the
model's answer.

The reports identify the model by tag, not model digest. They do not capture a
complete runtime environment. The Gradio dependency is pinned, but its
transitive dependencies are not fully locked. Record model digest, Ollama
version, runtime versions, and hardware for future performance comparisons.

## Evaluation history

All three runs completed with no recorded request errors or invalid JSON
outputs. These counts do not imply that all explanations or concern labels
were correct.

| Run | Dataset | Matches | Concerning references matched | No-clear-concern references matched | Insufficient-context references matched |
| --- | --- | --- | --- | --- | --- |
| v1 | Original 20 | 14/20 | 8/8 | 5/6 | 1/6 |
| v2 | Same original 20 | 17/20 | 8/8 | 5/6 | 4/6 |
| v2 | Additional 18 | 16/18 | 6/6 | 6/6 | 4/6 |

Reference report filenames, retained locally rather than included in this
documentation package:

- `evaluation_20261017T190023_714166Z.json` — v1, original 20.
- `evaluation_20261017T191607_666348Z.json` — v2, original 20.
- `evaluation_20261017T200635_371171Z.json` — v2, additional 18.

The first two runs used the same data, model, schema, and generation settings.
The third used the frozen v2 prompt on different synthetic examples. All
reference labels are provisional, and both sets are now development data.

### Evidence and automatic review

| Run | Responses containing evidence | All quotes exact among those responses | Review-flagged responses in the original report | Review-flagged responses under current checks |
| --- | --- | --- | --- | --- |
| v1, original 20 | 12 | 9/12 | 3 | 3 |
| v2, original 20 | 13 | 11/13 | 3 | 4 |
| v2, additional 18 | 11 | 10/11 | 2 | 4 |

Empty evidence arrays are excluded from the quote denominators above. A
verbatim quote can still be irrelevant to its label. The final column comes
from applying the current Python checks to recorded responses without new
model inference. It measures changed detection, not changed model behavior.

For the additional set, current checks flag `validation_005`, `validation_008`,
`validation_014`, and `validation_017`. The first three have evidence with no
concerns; the last quotes context as evidence. In the original v2 set, the
additional detected case is `case_016`.

## Verified browser workflow

The developer submitted the password-request example through the browser and
uploaded `analysis_20261024T230616_864587Z.json` on October 24, 2026.

- The model returned `concerning`, appropriate for the password disclosure request.
- The raw response and parsed answer matched.
- Evidence was copied exactly from the message.
- Request errors, validation errors, and review flags were empty.
- The report recorded `elapsed_seconds: 66.325`.
- The explanation still called an existing account-block claim a threat to
  block the account. This reasoning error passed the structural checks.

Earlier interactive context checks used the same money-request text with and
without repayment context. The assessments were `insufficient_context` and
`no_clear_concern`, respectively. The no-context response included evidence
with empty concerns, which the revised check detected. Reported times were
53.8 and 10.2 seconds. These observations do not isolate the causes of latency.

During implementation, recorded responses and simulated errors were used to
check shared inference, validation, report saving, and interface behavior.
The real Gradio server and queued HTTP endpoint were exercised with simulated
model responses; those checks were not new model evaluations. These development
checks are recorded here; a reusable test suite is future repository work.

## Known issues to preserve for follow-up

| ID | Observation | Source and consequence |
| --- | --- | --- |
| B01 | Account-status claim labeled as a threat | Browser report and earlier CLI example: `threat_of_account_block` is unsupported by a statement that the account is already blocked. |
| B02 | Legitimate code notification overflagged | Original v2 `case_006` supplies a user-requested reset code but was classified as concerning. A different notification wording passed in `validation_001`; the earlier failure is not resolved. |
| B03 | Threat direction reversed in explanation | `validation_010` threatens harm if the recipient leaves; the explanation describes compliance with leaving. The concerning assessment still matches. |
| B04 | Extra labels and wrong evidence source | `validation_017` adds an immediate-payment label without a stated deadline and copies context into evidence. Exact-quote validation catches the source problem, not every unsupported label. |
| B05 | Evidence with no concerns | Revised checks catch this in `validation_005`, `008`, and `014`. Detection is improved; the generated answers remain inconsistent. |
| B06 | Missing emotional-pressure observation | `validation_015` matches insufficient context but does not identify the wording linking family support to agreement. |
| B07 | Reference-policy ambiguity | Privacy request `validation_007` and ID request `validation_013` disagree with their references. Clarify the rubric before treating each disagreement as an indisputable model error. |

## Dataset identity

SHA-256 values refer to the exact files used by the recorded evaluations:

`data/test_cases.json` — 20 cases:

```text
dd7f8280211b72693e8c04a19d94a09a827b0a76aed4e6fb66dac74254e961c1
```

`data/validation_cases.json` — 18 cases:

```text
4565d19c030df09fade445dae2745444a15bc2fd16150d13a54e64c5bfe0997b
```

Whitespace or line-ending changes can alter a byte hash without changing JSON
values. The supplied `.gitattributes` requests LF checkouts for JSON and source
files. Evaluation reports preserve their own dataset hashes.

## Comparison procedure for the next change

1. Commit and tag the working baseline using [GIT_SETUP.md](GIT_SETUP.md).
2. State the specific failure being addressed and clarify any disputed labels.
3. Make one coherent change on a branch, recording the new prompt version if
   the model instructions change.
4. Run both datasets with the same model and generation settings when assessing
   a prompt change. Keep all reports locally.
5. Compare newly fixed cases, regressions, quote violations, and explanation
   quality. Do not accept a higher headline score as the only success criterion.
