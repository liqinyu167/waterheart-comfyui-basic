#!/usr/bin/env python3
"""Manage local Windows ComfyUI runtime from WSL."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def discover_windows_host() -> str:
    route = subprocess.run(
        ["ip", "route", "show", "default"],
        check=False,
        capture_output=True,
        text=True,
    )
    if route.returncode == 0:
        parts = route.stdout.strip().split()
        if "via" in parts:
            return parts[parts.index("via") + 1]
    raise RuntimeError("Unable to discover Windows host IP from WSL default route")


def build_base_url(config: dict[str, Any], host: str | None = None) -> str:
    host = host or discover_windows_host()
    port = config["comfy"]["port"]
    return f"http://{host}:{port}"


def health_check(config: dict[str, Any], host: str | None = None, timeout: int = 3) -> dict[str, Any]:
    base_url = build_base_url(config, host)
    endpoint = config["comfy"]["health_endpoint"]
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=timeout)
        response.raise_for_status()
        return {
            "ok": True,
            "status": "ready",
            "host": base_url,
            "http_status": response.status_code,
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": "down",
            "host": base_url,
            "error": str(exc),
        }


def run_windows_command(command: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [
            "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
            "-NoProfile",
            "-Command",
            command,
        ],
        check=False,
        capture_output=True,
    )
    # Decode with error handling for Windows encoding issues
    stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
    stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
    return subprocess.CompletedProcess(
        args=result.args,
        returncode=result.returncode,
        stdout=stdout,
        stderr=stderr,
    )


def start_comfy(config: dict[str, Any]) -> dict[str, Any]:
    task_name = config["comfy"]["task_name"]
    start_result = run_windows_command(f'schtasks /run /tn "{task_name}"')
    if start_result.returncode != 0:
        return {
            "ok": False,
            "status": "start_failed",
            "stderr": start_result.stderr.strip(),
            "stdout": start_result.stdout.strip(),
        }

    deadline = time.time() + config["comfy"]["startup_timeout_seconds"]
    while time.time() < deadline:
        status = health_check(config)
        if status["ok"]:
            status["started"] = True
            return status
        time.sleep(config["comfy"]["startup_poll_seconds"])

    return {
        "ok": False,
        "status": "timeout",
        "host": build_base_url(config),
        "error": "ComfyUI did not become ready before timeout",
    }


def ensure_ready(config: dict[str, Any]) -> dict[str, Any]:
    status = health_check(config)
    if status["ok"]:
        status["started"] = False
        return status
    return start_comfy(config)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage local Windows ComfyUI runtime from WSL.")
    parser.add_argument("action", choices=["status", "start", "ensure-ready", "host"])
    args = parser.parse_args()

    config = load_config()

    if args.action == "host":
        print(json.dumps({"host": discover_windows_host()}, ensure_ascii=False))
        return 0
    if args.action == "status":
        print(json.dumps(health_check(config), ensure_ascii=False))
        return 0
    if args.action == "start":
        print(json.dumps(start_comfy(config), ensure_ascii=False))
        return 0
    if args.action == "ensure-ready":
        print(json.dumps(ensure_ready(config), ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
