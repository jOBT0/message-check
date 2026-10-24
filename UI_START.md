# Run your suspicious-message analyzer in a browser

Your two payment examples behaved as expected under the current policy:

| Input | Assessment | Output check |
| --- | --- | --- |
| Money request with no context | Insufficient context | Correctly warned about evidence with no concerns |
| Same request with an agreed repayment | No clear concern | Passed the automatic format checks |

The second response took 10.2 seconds, compared with 53.8 seconds for the first.
Those measurements show variable latency; they do not isolate the cause.
The first response still violated the evidence rule. The validator detected it
and preserved the answer for review. We keep that limitation visible in the UI.

## 1. Add these files to AI_Project

Download `app.py`, `requirements-ui.txt`, and this guide. Put them in your
`AI_Project` folder beside the updated `evaluate_v2.py` and `analyze.py` from
the previous step. The Python files belong in the project root, not in `data`.

The existing evaluator, CLI, model, prompt, datasets, and reports stay as they
are. The new interface imports the same `analyze_message(...)` function and
the existing report-saving function.

## 2. Install the interface dependency once

Open PowerShell inside `AI_Project`. Check your Python version:

```powershell
py --version
```

Gradio requires Python 3.10 or newer. If you have an older interpreter, install
a supported Python release from https://www.python.org/downloads/ and reopen
PowerShell before continuing.

Create a virtual environment for this project, then install the UI dependency:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt
```

If the project already uses a suitable `.venv`, skip the creation command and
use that environment. A virtual environment keeps this project's Python
packages together. These commands call its interpreter directly, so activation
is unnecessary.

The file pins Gradio to version 6.30.0. Installing it also installs its required
dependencies; the model is still the one already downloaded by Ollama.

## 3. Start the app

Open Ollama as usual. In the same PowerShell window, run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Your browser should open the local interface. If it does not, visit:

http://127.0.0.1:7860

Keep PowerShell running while using the page. Stop the server with Ctrl+C in
PowerShell when finished. On later visits, you only need to open Ollama and run
the launch command again; dependency installation is a one-time step unless
the environment is recreated or dependencies change.

## 4. Use it

1. Paste a short message into **Message**.
2. Add relevant background in **Context**, or leave it empty.
3. Click **Analyze message** and wait for the result.
4. Read **Checks and warnings** as well as the assessment and explanation.

You no longer need `/done` or `/quit` in the browser. The sample rows populate
the inputs but do not run the model until you click the analysis button.

The right side shows the assessment, explanation, concerns, exact quoted
evidence, and elapsed time. The **Full response for review** panel includes
the input and raw model response. Model-generated text is displayed in plain
text fields, not rendered as model-supplied HTML.

If **Save a JSON report in results** is checked, the app creates a new
`results/analysis_<timestamp>.json` after the request. It includes the entered
message and context. Saving is off by default. Existing reports are not
overwritten. A save failure is shown as a separate notice.

The interface binds to `127.0.0.1`, uses `share=False`, and disables Gradio
analytics. It calls the same local Ollama endpoint as the terminal analyzer.
This step runs the interface on your computer; hosting it elsewhere would
require a separate plan for running or reaching the model.

## 5. What this step adds

You now have three ways to use the same analysis function:

| Entry point | Purpose |
| --- | --- |
| `evaluate_v2.py` | Score the synthetic test cases and review reports |
| `analyze.py` | Analyze messages interactively in the terminal |
| `app.py` | Analyze messages using a local browser interface |

The interface does not improve the model's reasoning. Inconsistent answers
remain visible with warnings. A response that passes automatic checks still
needs human review, and no clear concern does not establish safety.

## Verification completed for this step

The interface was built and served with Gradio 6.30.0 and Python 3.12. The actual
queued HTTP endpoint was exercised using simulated model responses for the two
context variants. Empty input, warning display, request errors, malformed JSON,
and optional report saving were also checked. No live Ollama inference was run
here, and the Windows launch commands still need their first run on your laptop.

## Troubleshooting

- **Gradio is missing:** run the install command with the same `.venv` Python
  shown above, then launch with that interpreter too.
- **The updated analyzer files are missing:** keep `evaluate_v2.py`, `analyze.py`,
  and `app.py` together in the project root.
- **Ollama cannot be reached:** open Ollama and retry. The same installed model
  used by your terminal tests must be available.
- **Port 7860 is already in use:** stop an earlier copy, or launch on another
  local port with `.\.venv\Scripts\python.exe app.py --port 7861` and visit
  http://127.0.0.1:7861.
- **The first request takes a while:** allow it to finish. The request timeout
  is 300 seconds. Requests are queued one at a time.
- **A review warning appears:** inspect the explanation, concerns, and quoted
  evidence; the answer is intentionally preserved rather than silently edited.

## Sources

- Gradio package, version and Python requirement:
  https://pypi.org/project/gradio/6.30.0/
- Gradio documentation: https://www.gradio.app/docs
