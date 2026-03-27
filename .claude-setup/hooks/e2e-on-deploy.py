#!/usr/bin/env python3
"""PostToolUse hook for Bash: E2E health check after deploy commands.

Triggers when bash command contains "deploy", "docker compose up",
or "docker-compose up". Curls /health endpoint and reports status.

stdlib only, fast, defensive — never crashes.
"""

import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEPLOY_PATTERNS = [
    r"\bdeploy\b",
    r"docker[\s-]compose\s+up",
]

# Common deploy targets — try to detect URL from command context
URL_PATTERNS = [
    # ssh user@host "... curl http://localhost:PORT/health"
    r"https?://[\w.:/-]+",
    # localhost with port
    r"localhost:\d+",
    # IP with port
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+",
    # IP without port (assume 80/443)
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
]

# Known deploy targets from infra
KNOWN_TARGETS = {
    "aragant": "http://94.198.219.232:8000/health",
    "bionovacia": "http://94.198.219.232:8002/health",
}


def is_deploy_command(command: str) -> bool:
    """Check if bash command is deploy-related."""
    cmd_lower = command.lower()
    return any(re.search(p, cmd_lower) for p in DEPLOY_PATTERNS)


def extract_url(command: str) -> str | None:
    """Try to extract a deployable URL from the command."""
    # Check known project names first
    cmd_lower = command.lower()
    for project, url in KNOWN_TARGETS.items():
        if project in cmd_lower:
            return url

    # Try to find explicit URLs
    for pattern in URL_PATTERNS:
        match = re.search(pattern, command)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = f"http://{url}"
            if "/health" not in url:
                url = url.rstrip("/") + "/health"
            return url

    return None


def check_health(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    """Curl the /health endpoint. Returns (ok, detail)."""
    try:
        req = Request(url, method="GET")
        resp = urlopen(req, timeout=timeout)
        body = resp.read(4096).decode("utf-8", errors="replace")
        return True, body[:200]
    except HTTPError as e:
        return False, f"HTTP {e.code}"
    except URLError as e:
        reason = str(getattr(e, "reason", e))[:100]
        return False, f"Connection failed: {reason}"
    except Exception as e:
        return False, str(e)[:100]


def main() -> None:
    try:
        raw = sys.stdin.read()
    except Exception:
        return

    if not raw.strip():
        return

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return

    # PostToolUse hook: check tool_name and tool_input
    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        return

    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command or not is_deploy_command(command):
        return

    print("\nE2E check after deploy...")

    url = extract_url(command)
    if not url:
        print("Could not detect deploy URL from command.")
        print("Suggest: run /qa-verify for full verification.")
        return

    print(f"Checking: {url}")
    ok, detail = check_health(url)

    if ok:
        print(f"Health check passed: {detail[:80]}")
    else:
        print(f"Health check FAILED: {detail}")
        print("Check deploy logs and service status!")

    print("Run /qa-verify for full QA verification.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never crash — hooks must be silent on failure
        pass
