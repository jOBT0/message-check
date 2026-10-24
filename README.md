# Message Check

A local AI prototype that explains warning signs in suspicious messages. It
uses a pretrained language model to assess supplied text and optional context,
quote supporting evidence, and describe uncertainty.

The project covers scams, impersonation, threats, and coercive pressure. Its
purpose is to help someone understand a message, without claiming to know the
sender's intentions or verifying the sender's identity.

**Status:** working local prototype. A browser submission, model response,
validation, and saved JSON report were verified on October 24, 2026. The current
behavior is documented in [BASELINE.md](BASELINE.md).

## What it does

- Accepts a message and optional context through a browser or terminal.
- Returns an assessment, concern labels, exact evidence quotes, and explanation.
- Checks JSON structure and consistency, then displays review warnings.
- Preserves the model's original answer, including answers that need review.
- Optionally saves each analysis as a separate JSON report.
- Evaluates assessment agreement against two synthetic datasets, totaling 38 cases.

The model is prompted, not fine-tuned. The examples are evaluation references;
their expected answers are never included in model requests.

## Requirements and setup

- Python 3.10 or newer for the complete app.
- Ollama installed and running locally.
- Model: `qwen3:4b-instruct-2507-q4_K_M`.
- Gradio 6.30.0, pinned in `requirements-ui.txt`.

From a PowerShell terminal in the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt
```

Reuse a suitable existing `.venv` if one is already present. For a fresh model
installation, open Ollama and download the configured model:

```powershell
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

The default configuration calls the local Ollama chat endpoint at
`http://127.0.0.1:11434/api/chat`.

## Run the browser interface

Open Ollama, then run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Visit [http://127.0.0.1:7860](http://127.0.0.1:7860) if the browser does not open
automatically. Enter a message, optionally add context, and select **Analyze
message**. Keep the terminal open; Ctrl+C stops the server.

The sample rows fill the inputs without making a model request. Select **Save
a JSON report in results** to retain the input, context, raw response, checks,
and timing in `results/analysis_<timestamp>.json`. Saving is off by default.

The interface binds to loopback, disables Gradio analytics, and uses
`share=False`. Hosting the interface elsewhere would require a separate model
deployment or connection arrangement.

## Run the terminal analyzer

```powershell
.\.venv\Scripts\python.exe analyze.py
```

Paste a message, type `/done` on a new line, and enter optional context. Type
`/quit` at the message prompt to exit. Add `--save` to write reports, or supply
a single message directly:

```powershell
.\.venv\Scripts\python.exe analyze.py --message 'Can you send me the money today?' --context 'A friend reminding me about a repayment we agreed on yesterday.'
```

The terminal analyzer and evaluator use the Python standard library; Gradio is
needed only for the browser interface.

## Interpret the output

| Field or assessment | Meaning |
| --- | --- |
| `concerning` | Concrete warning signs warrant concern. |
| `insufficient_context` | Missing information could materially change the assessment. |
| `no_clear_concern` | No clear warning signs were identified in the supplied information; safety is not verified. |
| `concerns` | Specific observations or tentative concern labels. |
| `evidence` | Exact substrings from the message itself, not from context. |
| `explanation` | The model's reasoning and material uncertainty. |

Automatic checks validate fields and types, exact quotes, inconsistent
concern/evidence arrays, and output-token truncation. They cannot establish
whether an explanation is semantically correct. A result with no review flags
can still contain an unsupported label or a misunderstanding.

## Evaluate a change

Run both sets after changing the prompt or model:

```powershell
.\.venv\Scripts\python.exe evaluate_v2.py --cases data/test_cases.json
.\.venv\Scripts\python.exe evaluate_v2.py --cases data/validation_cases.json
```

Each run creates a timestamped report in `results/` and saves progress after
each response. Reports include the prompt, settings, data hash, raw answers,
validation findings, and assessment comparisons. `--limit 2` can be added when
checking that a newly configured environment runs successfully.

Recorded results from October 17, 2026:

| Prompt | Dataset | Assessment agreement |
| --- | --- | --- |
| v1 | Original 20 cases | 14/20 (70.0%) |
| v2 | Same original 20 cases | 17/20 (85.0%) |
| v2 | Additional 18 cases | 16/18 (88.9%) |

These are agreements with provisional labels on small synthetic datasets,
not real-world reliability estimates. The original set informed prompt
development. The additional set targeted known weaknesses and has also been
reviewed during development. Its percentage cannot be interpreted as an
improvement over a score on different messages. See [BASELINE.md](BASELINE.md)
for class breakdowns and explanation errors that the headline scores miss.

## Project files

| Path | Purpose |
| --- | --- |
| `app.py` | Gradio browser interface. |
| `analyze.py` | Interactive CLI and report-saving function. |
| `evaluate_v2.py` | Current prompt, inference, shared checks, and evaluation CLI. |
| `evaluate.py` | Historical v1 evaluator for comparison. |
| `requirements-ui.txt` | Pinned Gradio dependency. |
| `data/test_cases.json` | Original 20 synthetic cases. |
| `data/validation_cases.json` | Additional 18 synthetic cases. |
| `results/` | Generated reports; excluded from new Git tracking. |
| `BASELINE.md` | Recorded settings, evidence, scores, and known issues. |
| `GIT_SETUP.md` | Instructions for the first local commit and version tag. |
| `.gitignore` | Excludes environments, generated reports, local settings, and caches. |
| `.gitattributes` | Requests LF line endings for tracked source, documentation, and JSON. |

Both interfaces call `analyze_message()` from `evaluate_v2.py`. The evaluator
adds expected-answer scoring only after that function returns. The browser
reuses the CLI's report-saving function. This layout is intentionally small;
extracting a dedicated analysis module is a possible later refactor.

## Known limitations and next development work

- The model can invent labels, mistake an account-status claim for a threat,
  or reverse the meaning of a sentence even when the assessment matches.
- It has sometimes misclassified a legitimate login-code notification.
- Context and exact-quote checks help, but do not verify identities, links,
  attachments, intent, or the truth of supplied context.
- Responses may omit supported emotional-pressure cues or disagree with
  debatable reference labels for privacy and identity-document requests.
- Latency varies. One saved browser request took 66.3 seconds; that is one
  observation, not a performance benchmark.

Next work: clarify the assessment rubric, add repeatable tests for the shared
checks, and make targeted prompt changes on a branch while rerunning both
datasets and manually reviewing explanations. Preserve this baseline for
comparison. Raw reports may contain personal messages, so the documented
synthetic summaries are tracked separately from generated results.

## References

- [Ollama CLI documentation](https://docs.ollama.com/cli)
- [Gradio 6.30.0 package](https://pypi.org/project/gradio/6.30.0/)
- [Git setup for this project](GIT_SETUP.md)
