#!/usr/bin/env python3
"""
Telegram notification helper for Claude Code learning system.
Used by daily-review, good-morning, and session-summarizer.

Usage:
  echo "message text" | python3 telegram-notify.py
  python3 telegram-notify.py "message text"
  python3 telegram-notify.py --file /path/to/report.md
"""
import os
import sys
import urllib.request
import urllib.parse
import json

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_USER_ID", "")

def send_message(text: str, parse_mode: str = "Markdown") -> bool:
    """Send a message via Telegram Bot API."""
    if not BOT_TOKEN or not CHAT_ID:
        print("[telegram-notify] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_USER_ID", file=sys.stderr)
        return False

    # Truncate to Telegram limit (4096 chars)
    if len(text) > 4000:
        text = text[:3950] + "\n\n... (truncated)"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                return True
            else:
                print(f"[telegram-notify] API error: {result}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"[telegram-notify] Failed: {e}", file=sys.stderr)
        return False

def main():
    text = ""

    if len(sys.argv) > 1:
        if sys.argv[1] == "--file" and len(sys.argv) > 2:
            try:
                with open(sys.argv[2]) as f:
                    text = f.read()
            except Exception as e:
                print(f"Error reading file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            text = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        text = sys.stdin.read()

    if not text.strip():
        print("Usage: telegram-notify.py 'message' | --file path | pipe stdin", file=sys.stderr)
        sys.exit(1)

    ok = send_message(text.strip())
    if ok:
        print("Sent to Telegram")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
