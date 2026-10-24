"""Interactively explain suspicious messages with the existing local model.

Requires the updated evaluate_v2.py in the same folder and Python 3.9+.
Uses only the Python standard library; there is nothing to install with pip.

    py analyze.py
    py analyze.py --message "Can you send the money today?"
    py analyze.py --save

The default displays results without writing analysis files. --save includes
the entered message, context, and raw model response in a new results file.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from evaluate_v2 import (
        DEFAULT_MODEL,
        OPTIONS,
        PROMPT_VERSION,
        VALIDATION_VERSION,
        analyze_message,
    )
except ImportError as exc:
    raise SystemExit(
        "Place the UPDATED evaluate_v2.py in the same folder as analyze.py. "
        "Download both files from this project step."
    ) from exc


RESULTS_DIR = Path(__file__).resolve().parent / "results"
LABELS = {
    "concerning": "Concerning",
    "no_clear_concern": "No clear concern",
    "insufficient_context": "Insufficient context",
}


def read_message():
    """Accept multiline messages, including blank lines, without carrying history."""
    print("\nPaste a message, then type /done on a new line and press Enter.")
    print("Type /quit on its own line to exit.")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            return "\n".join(lines) if lines else None
        if line.strip() == "/quit":
            return None
        if line.strip() == "/done":
            return "\n".join(lines)
        lines.append(line)


def print_result(record):
    """Display problems before presenting a structurally valid model answer."""
    if record["request_error"]:
        print("\nAnalysis failed: " + record["request_error"])
        return
    if record["validation_errors"]:
        print("\nThe model returned an invalid response:")
        for error in record["validation_errors"]:
            print("- " + error)
        print("\nRaw model response:")
        print(record["raw_response"])
        return

    if record["review_flags"]:
        print("\nREVIEW NEEDED - this response has consistency problems:")
        for flag in record["review_flags"]:
            print("- " + flag)
        print("The model's answer is shown below as returned.")

    analysis = record["analysis"]
    print("\nAssessment: " + LABELS[analysis["assessment"]])
    print("Concerns:")
    for concern in analysis["concerns"]:
        print("- " + concern)
    if not analysis["concerns"]:
        print("- None listed")
    print("Evidence:")
    for quote in analysis["evidence"]:
        print("- " + json.dumps(quote, ensure_ascii=False))
    if not analysis["evidence"]:
        print("- None listed")
    print("Explanation: " + analysis["explanation"])
    print(f"Time: {record['elapsed_seconds']:.1f} seconds")
    if not record["review_flags"]:
        print("Automatic format checks passed; the reasoning still needs review.")
    if analysis["assessment"] == "no_clear_concern":
        print("No clear concern does not verify that the message or sender is safe.")


def save_result(record):
    """Create a separate file for each analysis; never overwrite an older result."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    path = RESULTS_DIR / ("analysis_" + timestamp + ".json")
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return path


def run_once(message, context, args):
    if not args.json:
        print("\nAnalyzing... The first request can take longer.", flush=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": DEFAULT_MODEL,
        "prompt_version": PROMPT_VERSION,
        "validation_version": VALIDATION_VERSION,
        "options": dict(OPTIONS),
    }
    record.update(analyze_message(message, context, timeout=args.timeout))
    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=False))
    else:
        print_result(record)
    if args.save:
        try:
            path = save_result(record)
        except OSError as exc:
            print(f"Could not save the analysis: {exc}", file=sys.stderr)
            return 1
        print(f"Saved: {path}", file=sys.stderr if args.json else sys.stdout)
    if record["request_error"] or record["validation_errors"]:
        return 1
    return 2 if record["review_flags"] else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--message", help="Analyze one message and exit instead of opening the interactive loop.")
    parser.add_argument("--context", help="Optional background for --message; omit it when unknown.")
    parser.add_argument("--save", action="store_true", help="Save each analysis, including its input, in results/.")
    parser.add_argument("--json", action="store_true", help="Print the full JSON record; requires --message.")
    parser.add_argument("--timeout", type=int, default=300, help="Seconds allowed per request (default: 300).")
    args = parser.parse_args(argv)
    if args.timeout < 1:
        parser.error("--timeout must be positive.")
    if args.message is not None and not args.message.strip():
        parser.error("--message must not be empty.")
    if args.message is None and (args.context is not None or args.json):
        parser.error("--context and --json require --message.")
    try:
        if args.message is not None:
            return run_once(args.message, args.context if args.context and args.context.strip() else None, args)
        print("Suspicious-message analyzer")
        print(f"Model: {DEFAULT_MODEL} | Prompt: {PROMPT_VERSION}")
        print("Each analysis uses only the current message and context.")
        while True:
            message = read_message()
            if message is None:
                return 0
            if not message.strip():
                print("Please enter a message before /done.")
                continue
            try:
                context = input("Context (optional, one line; press Enter to skip): ")
            except EOFError:
                context = ""
            run_once(message, context if context.strip() else None, args)
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
