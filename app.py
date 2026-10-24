"""A local Gradio interface for the suspicious-message analyzer.

Keep the updated evaluate_v2.py and analyze.py beside this file.
Install requirements-ui.txt, open Ollama, then run this file with Python.
The model, prompt, and output checks are imported from the existing project.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Apply before importing Gradio. The interface is served on loopback only.
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

try:
    from evaluate_v2 import (
        DEFAULT_MODEL,
        OPTIONS,
        PROMPT_VERSION,
        VALIDATION_VERSION,
        analyze_message,
    )
    from analyze import save_result
except ImportError as exc:
    raise SystemExit(
        "Keep the updated evaluate_v2.py and analyze.py beside app.py."
    ) from exc


LABELS = {
    "concerning": "Concerning",
    "insufficient_context": "Insufficient context",
    "no_clear_concern": "No clear concern (does not verify safety)",
}


def display_record(record, save_notice=""):
    """Return plain text fields and the complete record, without repairing answers."""
    timing = f"{record['elapsed_seconds']:.1f} seconds"
    if record["request_error"]:
        checks = "Analysis failed.\n" + record["request_error"]
        return (checks + save_notice, "", "", "", "", timing, record)
    if record["validation_errors"]:
        checks = "Invalid model response.\n" + "\n".join(record["validation_errors"])
        return (checks + save_notice, "", "", "", "", timing, record)
    if record["review_flags"]:
        checks = "REVIEW NEEDED\n" + "\n".join("- " + flag for flag in record["review_flags"])
        checks += "\nThe model's answer is shown as returned."
    else:
        checks = "Automatic format checks passed. The reasoning still needs review."
    analysis = record["analysis"]
    return (
        checks + save_notice,
        LABELS[analysis["assessment"]],
        "\n".join("- " + label for label in analysis["concerns"]) or "None listed",
        "\n\n".join(json.dumps(quote, ensure_ascii=False) for quote in analysis["evidence"]) or "None listed",
        analysis["explanation"],
        timing,
        record,
    )


def analyze_for_ui(message, context, save_report):
    """Clear old results immediately, then run one independent analysis."""
    if not isinstance(message, str) or not message.strip():
        yield ("Enter a message before analyzing.", "", "", "", "", "", {})
        return
    if context is not None and not isinstance(context, str):
        yield ("Context must be text or left empty.", "", "", "", "", "", {})
        return
    context = context if context and context.strip() else None
    yield ("Analyzing... The first request can take longer.", "", "", "", "", "", {})
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": DEFAULT_MODEL,
        "prompt_version": PROMPT_VERSION,
        "validation_version": VALIDATION_VERSION,
        "options": dict(OPTIONS),
    }
    record.update(analyze_message(message, context, timeout=300))
    save_notice = ""
    if save_report:
        try:
            path = save_result(record)
        except OSError as exc:
            save_notice = f"\nReport could not be saved: {exc}"
        else:
            save_notice = f"\nSaved: {path}"
    yield display_record(record, save_notice)


def build_app():
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError(
            "Could not load Gradio. Install requirements-ui.txt using the same "
            f"Python environment that runs app.py. Details: {exc}"
        ) from exc

    with gr.Blocks(title="Message Check", analytics_enabled=False) as demo:
        gr.Markdown("# Message Check\nUnderstand warning signs in a message and what remains uncertain.")
        with gr.Row():
            with gr.Column():
                message = gr.Textbox(
                    label="Message",
                    placeholder="Paste the message you want to understand.",
                    lines=8,
                    max_lines=18,
                )
                context = gr.Textbox(
                    label="Context (optional)",
                    placeholder="Who sent it? Were you expecting it? Leave this empty if unknown.",
                    lines=3,
                )
                gr.Markdown("Each analysis uses only this message and the context you provide.")
                save_report = gr.Checkbox(
                    label="Save a JSON report in results (includes the entered text)",
                    value=False,
                )
                submit = gr.Button("Analyze message", variant="primary")
                gr.Examples(
                    examples=[
                        ["Your account is blocked. Reply with your password to restore access.",
                         "An unexpected message from someone claiming to provide account support."],
                        ["Can you send me the money today?", ""],
                        ["Can you send me the money today?",
                         "A friend reminding me about a repayment we agreed I would make today."],
                    ],
                    inputs=[message, context],
                    cache_examples=False,
                    label="Try a synthetic example",
                )
            with gr.Column():
                checks = gr.Textbox(label="Checks and warnings", value="Ready to analyze.", lines=3, interactive=False)
                assessment = gr.Textbox(label="Assessment", interactive=False)
                explanation = gr.Textbox(label="Explanation", lines=4, interactive=False)
                concerns = gr.Textbox(label="Concerns", lines=3, interactive=False)
                evidence = gr.Textbox(label="Quoted evidence", lines=4, interactive=False)
                timing = gr.Textbox(label="Response time", interactive=False)
        with gr.Accordion("Full response for review", open=False):
            raw_record = gr.JSON(label="Analysis record")
        gr.Markdown(
            "This prototype analyzes the supplied text. It does not verify the sender, "
            "open links, or establish whether a message is safe."
        )
        submit.click(
            fn=analyze_for_ui,
            inputs=[message, context, save_report],
            outputs=[checks, assessment, concerns, evidence, explanation, timing, raw_record],
            concurrency_limit=1,
            trigger_mode="once",
            api_name="analyze",
        )
    # Serialize inference so several clicks do not run the model concurrently.
    return demo.queue(default_concurrency_limit=1, max_size=4)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=7860, help="Local port (default: 7860).")
    parser.add_argument("--no-browser", action="store_true", help="Print the address without opening a browser.")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 10):
        parser.error("This interface requires Python 3.10 or newer.")
    if not 1024 <= args.port <= 65535:
        parser.error("--port must be between 1024 and 65535.")
    try:
        demo = build_app()
        demo.launch(
            server_name="127.0.0.1",
            server_port=args.port,
            share=False,
            inbrowser=not args.no_browser,
        )
    except (RuntimeError, OSError) as exc:
        print(f"Could not start the interface: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
