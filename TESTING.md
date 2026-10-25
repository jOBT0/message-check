# Testing Message Check

This first suite tests the Python output checks and request boundary in the
current `evaluate_v2.py`. It includes the known regression where the model
quotes a money request while returning an empty `concerns` array.

## Install the files

Extract `message-check-tests.zip` directly into `AI_Project`. It contains:

- `tests/test_output_checks.py`
- `TESTING.md`

The `tests` folder should sit beside `app.py`, `analyze.py`, and `evaluate_v2.py`.
The archive contains no replacement application files or model downloads.
Keep the downloaded ZIP outside `AI_Project`, or delete that ZIP after extraction,
so it does not appear as an untracked project file.

## Run the tests

Open PowerShell in your project folder:

```powershell
Set-Location "C:\Users\jonat\AI_Project"
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

If you are not using the project virtual environment, use:

```powershell
py -m unittest discover -s tests -p "test_*.py" -v
```

This uses Python's built-in `unittest` and `unittest.mock`; no package installation
is required. Run it from `AI_Project` so Python can import `evaluate_v2.py`.
The suite is compatible with the project's Python 3.10+ requirement.

The final lines should report `Ran 20 tests` and `OK`. Some tests also check
several variants using subtests. `Ran 0 tests` means the test file was not
discovered; check its folder and ensure Windows did not append `.txt`.

Ollama and the browser app can both remain closed. All HTTP requests are replaced
with in-memory responses or simulated errors. An unexpected HTTP request causes
a test failure instead of contacting Ollama. The tests do not write analysis
reports to `results/`.

## What the tests cover

| Area | Examples |
| --- | --- |
| Output structure | Exactly four fields, supported assessment labels, correct array and text types |
| Consistency | Evidence with no concerns; concerns with no evidence; contradictory assessment and concern fields |
| Evidence | Exact message substrings, including Unicode and newlines; rejection of paraphrases and context-only quotes |
| Generation limits | A token-limit warning even when the returned JSON is valid |
| Error handling | Malformed JSON, invalid output structure, and a simulated connection failure |
| Output preservation | The original raw answer and parsed fields remain available when warnings are raised |
| Evaluation integrity | Reference answers stay out of model requests; each request receives only the current message and context |
| Input checks | Invalid inputs fail before an HTTP request is attempted |

The simulated answers are synthetic fixtures, not fresh model predictions.
Passing these tests does not establish scam-detection accuracy, explanation
quality, evidence relevance, sender identity, or resistance to prompt injection.
In particular, matching a quote exactly does not prove that the quote supports
the assessment.

Keep using the existing evaluation scripts and human review for model behavior.
There is no need to rerun the 38 development examples merely to add these tests;
the prompt, settings, and application code are unchanged by this addition.

## Understand a failure

Read the failing test's name and assertion. For example,
`test_flags_evidence_without_concerns_for_every_assessment` protects the warning
that caught the inconsistent money-request answer.

The suite targets the current engine with `VALIDATION_VERSION = "output-checks-v2"`.
If `evaluate_v2.py` cannot be imported, check the current folder and file placement.
If a test fails, preserve its output and investigate the behavior before changing
the expected result. Several tests assert the user-facing warning text because
the current engine does not provide separate warning codes.

## Save the passing tests in Git

From `AI_Project`, check the repository root before staging:

```powershell
git rev-parse --show-toplevel
```

It must be `C:/Users/jonat/AI_Project`. Then stage just this addition:

```powershell
git add -- tests/test_output_checks.py TESTING.md
git diff --cached --stat
git diff --cached --name-only
```

The staged list should contain only those two new files. After the tests pass
and you have reviewed that list:

```powershell
git commit -m "Add offline regression tests for output checks"
git push
```

The push uses the upstream configured when you uploaded `main`. If Git reports
an error, stop and inspect it; do not use a force push. The existing `v0.1.0` tag
continues to identify the earlier application baseline, so do not move that tag.
