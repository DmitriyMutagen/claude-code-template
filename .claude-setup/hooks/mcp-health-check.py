#!/usr/bin/env python3
"""MCP health check for Claude Code SessionStart hook.

Quickly verifies critical MCP servers are configured and reachable.
Prints a summary line to stdout (injected into Claude context).
Designed to run in <3 seconds, never crash, never block session start.
"""

import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
TOTAL_TIMEOUT = 3.0


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def check_env_var(env: dict, var_name: str, label: str) -> tuple[str, bool, str]:
    """Check if an env var exists in settings env block or os.environ."""
    if env.get(var_name) or os.environ.get(var_name):
        return (label, True, "")
    return (label, False, f"env {var_name} not set")


def check_binary(command: str, label: str) -> tuple[str, bool, str]:
    """Check if a command binary is findable on PATH or is absolute."""
    if command in ("npx", "uvx", "uv", "node", "python", "python3"):
        return (label, True, "")
    p = Path(command)
    if p.is_absolute():
        if p.exists():
            return (label, True, "")
        return (label, False, f"binary not found ({command})")
    # Check PATH
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if (Path(d) / command).exists():
            return (label, True, "")
    return (label, False, f"binary not found ({command})")


def check_http(url: str, label: str, timeout: float = 2.0) -> tuple[str, bool, str]:
    """Quick HEAD/GET to verify HTTP MCP is reachable.

    Any HTTP response (even 4xx/5xx) means the server is alive.
    Only network-level failures count as unhealthy.
    """
    from urllib.error import HTTPError

    try:
        req = Request(url, method="HEAD")
        urlopen(req, timeout=timeout)
        return (label, True, "")
    except HTTPError:
        # Server responded with an error code -- but it IS reachable
        return (label, True, "")
    except URLError as e:
        reason = str(getattr(e, "reason", e))[:60]
        return (label, False, f"connection failed ({reason})")
    except Exception as e:
        return (label, False, str(e)[:60])


def main() -> None:
    start = time.monotonic()
    settings = load_settings()
    if not settings:
        print("MCP Status: cannot read settings.json")
        return

    env_block = settings.get("env", {})
    mcp_servers = settings.get("mcpServers", {})
    results: list[tuple[str, bool, str]] = []

    # --- Critical env-based checks ---
    results.append(check_env_var(env_block, "SENTRY_AUTH_TOKEN", "sentry"))
    results.append(check_env_var(env_block, "TELEGRAM_BOT_TOKEN", "telegram-notify"))
    results.append(check_env_var(env_block, "WB_API_TOKEN", "wildberries"))
    results.append(check_env_var(env_block, "SELLER_API_KEY", "ozon-marketplace"))
    results.append(check_env_var(env_block, "DATABASE_URL", "postgresql"))

    # --- Check configured MCP servers exist ---
    critical_mcps = [
        "sentry-mcp", "telegram-notify", "filesystem", "git",
        "github-mcp", "brave-search", "exa", "docker", "time",
    ]
    for name in critical_mcps:
        if (time.monotonic() - start) > TOTAL_TIMEOUT:
            break
        server = mcp_servers.get(name)
        if not server:
            results.append((name, False, "not in mcpServers config"))
            continue
        server_type = server.get("type", "")
        if server_type == "http":
            url = server.get("url", "")
            if url:
                results.append(check_http(url, name, timeout=2.0))
            else:
                results.append((name, False, "no url configured"))
        else:
            cmd = server.get("command", "")
            if cmd:
                results.append(check_binary(cmd, name))
            else:
                results.append((name, False, "no command configured"))

    # --- N8N reachability (HTTP) ---
    n8n_url = env_block.get("N8N_URL") or os.environ.get("N8N_URL", "")
    if n8n_url and (time.monotonic() - start) < TOTAL_TIMEOUT:
        remaining = max(0.5, TOTAL_TIMEOUT - (time.monotonic() - start))
        results.append(check_http(n8n_url, "n8n", timeout=min(remaining, 2.0)))
    elif n8n_url:
        results.append(("n8n", False, "skipped (timeout budget)"))
    else:
        results.append(("n8n", False, "N8N_URL not set"))

    # --- Deduplicate by label (keep first occurrence) ---
    seen: set[str] = set()
    unique: list[tuple[str, bool, str]] = []
    for label, ok, msg in results:
        if label not in seen:
            seen.add(label)
            unique.append((label, ok, msg))

    healthy = sum(1 for _, ok, _ in unique if ok)
    total = len(unique)
    failures = [(label, msg) for label, ok, msg in unique if not ok]

    if not failures:
        print(f"MCP Status: all {total} servers healthy")
    else:
        print(f"MCP Status: {healthy}/{total} healthy")
        for label, msg in failures:
            print(f"  ! {label}: {msg}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never crash, never block session start
        print("MCP Status: health check failed (internal error)")
        sys.exit(0)
