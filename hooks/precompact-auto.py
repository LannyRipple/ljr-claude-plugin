#!/usr/bin/env python3
"""
PreCompact auto hook — fires on automatic compaction.

Reads the session transcript, calls the Claude API to generate tailored
compaction instructions, writes them to /tmp/claude-502/compaction-instructions.md,
copies to clipboard, then exits with continue:false to halt compaction so the user
can run /compact manually with the generated instructions.
"""

import json
import os
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

RETAIN_DROP = (
    "Retain: work intent, decisions made, what was accomplished, any open questions.\n"
    "Drop: file contents, resolved errors, build logs, tool call details."
)

SYSTEM_PROMPT = (
    "You are summarizing a Claude Code session for compaction.\n"
    "Your output will be passed directly as compaction instructions.\n\n"
    "Write a structured summary using these sections (### headers; omit sections with nothing to say).\n\n"
    f"Start with this block verbatim:\n{RETAIN_DROP}\n\n"
    "Then write the sections:\n\n"
    "### User Intent\n"
    "What the user was trying to accomplish overall.\n\n"
    "### Completed Work\n"
    "What was finished. Include exact file paths, symbol names, and identifiers.\n\n"
    "### Errors & Corrections\n"
    "Mistakes made and how resolved. User corrections verbatim.\n\n"
    "### Active Work\n"
    "What was in progress when compaction triggered.\n\n"
    "### Pending Tasks\n"
    "Outstanding items not yet started.\n\n"
    "### Key References\n"
    "File paths, config values, identifiers, and constraints a resumed session needs.\n\n"
    "Preserve always: exact file paths, symbol names, error messages verbatim, user corrections, "
    "specific config values, technical constraints.\n\n"
    "Compression rules: weight recent messages more heavily; omit pleasantries, exploratory dead "
    "ends, and resolved errors already captured above; keep each section under 500 words; "
    "cut filler before cutting facts.\n\n"
    "If work was in progress when compaction triggered, end with a 'Next action:' line "
    "stating the specific next step — not a vague goal, but the concrete first action.\n\n"
    "Write in second person (you/your). No preamble or closing remarks."
)

OUTPUT_PATH = Path("/tmp/claude-502/compaction-instructions.md")
MAX_TURNS = 150  # cap to avoid sending the whole context back


def extract_turns(transcript_path: str) -> list[dict]:
    turns = []
    try:
        with open(transcript_path) as f:
            for line in f:
                entry = json.loads(line)
                etype = entry.get("type")
                if etype == "user":
                    msg = entry.get("message", {})
                    content = msg.get("content", "")
                    if isinstance(content, str) and content.strip():
                        turns.append({"role": "user", "content": content})
                elif etype == "assistant":
                    msg = entry.get("message", {})
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        text_parts = [
                            b.get("text", "")
                            for b in content
                            if isinstance(b, dict) and b.get("type") == "text"
                        ]
                        text = " ".join(text_parts).strip()
                    elif isinstance(content, str):
                        text = content.strip()
                    else:
                        text = ""
                    if text:
                        turns.append({"role": "assistant", "content": text})
    except Exception as e:
        sys.stderr.write(f"precompact-auto: transcript parse error: {e}\n")
    return turns[-MAX_TURNS:]


def call_claude(turns: list[dict]) -> str:
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
    bedrock_url = os.environ.get("ANTHROPIC_BEDROCK_BASE_URL", "")
    model = "claude-haiku-4-5-20251001"

    if bedrock_url:
        url = bedrock_url.rstrip("/") + "/v1/messages"
    else:
        url = "https://api.anthropic.com/v1/messages"

    transcript_text = "\n\n".join(
        f"[{t['role'].upper()}]: {t['content']}" for t in turns
    )

    payload = {
        "model": model,
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Here is the conversation transcript. "
                    "Write compaction instructions as described.\n\n"
                    f"{transcript_text}"
                ),
            }
        ],
    }

    body = json.dumps(payload).encode()
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    # Build SSL context honoring NODE_EXTRA_CA_CERTS (same cert bundle Claude Code uses)
    ca_bundle = os.environ.get("NODE_EXTRA_CA_CERTS")
    if ca_bundle and Path(ca_bundle).exists():
        ctx = ssl.create_default_context(cafile=ca_bundle)
    else:
        ctx = ssl.create_default_context()

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        data = json.loads(resp.read())

    content = data.get("content", [])
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            return block["text"]
    return ""


def write_output(text: str) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(text)


def copy_to_clipboard(text: str) -> None:
    try:
        proc = subprocess.run(["pbcopy"], input=text.encode(), check=True)
    except Exception as e:
        sys.stderr.write(f"precompact-auto: pbcopy failed: {e}\n")


def main() -> None:
    try:
        event = json.loads(sys.stdin.read())
    except Exception:
        # If we can't parse stdin, don't block — just exit cleanly
        sys.exit(0)

    transcript_path = event.get("transcript_path", "")

    if not transcript_path or not Path(transcript_path).exists():
        sys.stderr.write(f"precompact-auto: transcript not found: {transcript_path}\n")
        print(json.dumps({"continue": True}))
        return

    turns = extract_turns(transcript_path)

    if not turns:
        instructions = (
            f"{RETAIN_DROP}\n\n"
            "No conversation turns found in transcript. "
            "Add context manually before running /compact."
        )
    else:
        try:
            instructions = call_claude(turns)
        except Exception as e:
            sys.stderr.write(f"precompact-auto: API call failed: {e}\n")
            instructions = (
                f"{RETAIN_DROP}\n\n"
                f"[Hook error — API call failed: {e}]\n\n"
                "Add session context manually before running /compact."
            )

    write_output(instructions)
    copy_to_clipboard(instructions)

    result = {"continue": True}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
