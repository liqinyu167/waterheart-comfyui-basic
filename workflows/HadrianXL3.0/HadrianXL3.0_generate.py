#!/usr/bin/env python3
"""Generate images with the HadrianXL3.0 workflow."""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from comfy_manager import ensure_ready, load_config  # noqa: E402


WORKFLOW_PATH = Path(__file__).resolve().with_name("HadrianXL3.0.json")
PROMPT_BODY_NODE = "51"
SEED_NODE = "31"


def read_workflow() -> dict:
    return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))


def build_prompt(existing_prompt: str, visible_prompt: str) -> str:
    visible_prompt = visible_prompt.strip()
    if not existing_prompt.strip():
        return visible_prompt
    if not visible_prompt:
        return existing_prompt.strip()
    return f"{existing_prompt.strip()}, {visible_prompt}"


def inject_prompt(workflow: dict, visible_prompt: str) -> str:
    body_node = workflow.get(PROMPT_BODY_NODE)
    if not body_node or body_node.get("class_type") != "StringConstantMultiline":
        raise RuntimeError(f"Workflow prompt body node missing or invalid: {PROMPT_BODY_NODE}")

    existing = body_node.setdefault("inputs", {}).get("string", "")
    final_prompt = build_prompt(existing, visible_prompt)
    body_node["inputs"]["string"] = final_prompt
    return final_prompt


def inject_seed(workflow: dict, seed: int) -> None:
    seed_node = workflow.get(SEED_NODE)
    if not seed_node or "inputs" not in seed_node or "seed" not in seed_node["inputs"]:
        raise RuntimeError(f"Workflow seed node missing or invalid: {SEED_NODE}")
    seed_node["inputs"]["seed"] = seed


def submit_prompt(base_url: str, config: dict, workflow: dict) -> str:
    endpoint = config["comfy"]["prompt_endpoint"]
    response = requests.post(f"{base_url}{endpoint}", json={"prompt": workflow}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    prompt_id = payload.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI returned no prompt_id: {payload}")
    return prompt_id


def fetch_history(base_url: str, config: dict, prompt_id: str) -> dict:
    endpoint = config["comfy"]["history_endpoint"].format(prompt_id=prompt_id)
    response = requests.get(f"{base_url}{endpoint}", timeout=15)
    response.raise_for_status()
    return response.json()


def extract_images(history: dict, prompt_id: str) -> list[dict]:
    task = history.get(prompt_id, {})
    outputs = task.get("outputs", {})
    images: list[dict] = []
    for node_output in outputs.values():
        images.extend(node_output.get("images", []))
    return images


def wait_for_images(base_url: str, config: dict, prompt_id: str) -> list[dict]:
    deadline = time.time() + config["comfy"]["generation_timeout_seconds"]
    while time.time() < deadline:
        history = fetch_history(base_url, config, prompt_id)
        images = extract_images(history, prompt_id)
        if images:
            return images
        time.sleep(config["comfy"]["generation_poll_seconds"])
    raise TimeoutError(f"Timed out waiting for outputs for prompt_id={prompt_id}")


def download_image(base_url: str, config: dict, image: dict, output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    params = urlencode(
        {
            "filename": image["filename"],
            "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        }
    )
    endpoint = config["comfy"]["view_endpoint"]
    response = requests.get(f"{base_url}{endpoint}?{params}", timeout=60)
    response.raise_for_status()
    output_path = output_dir / image["filename"]
    output_path.write_bytes(response.content)
    return str(output_path)


def normalize_seed(raw_seed: str | None) -> int:
    if raw_seed is None or raw_seed == "random":
        return random.randint(1, 2**63 - 1)
    return int(raw_seed)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate with the HadrianXL3.0 workflow.")
    parser.add_argument("--prompt", required=True, help="Visible prompt text")
    parser.add_argument("--seed", default="random", help="Seed integer or 'random'")
    parser.add_argument("--dry-run", action="store_true", help="Validate prompt injection without sending to ComfyUI")
    args = parser.parse_args()

    config = load_config()
    workflow = copy.deepcopy(read_workflow())

    seed = normalize_seed(args.seed)
    final_prompt = inject_prompt(workflow, args.prompt)
    inject_seed(workflow, seed)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "ok": True,
                    "dry_run": True,
                    "workflow": "HadrianXL3.0",
                    "seed": seed,
                    "final_prompt": final_prompt,
                },
                ensure_ascii=False,
            )
        )
        return 0

    ready = ensure_ready(config)
    if not ready.get("ok"):
        print(json.dumps(ready, ensure_ascii=False))
        return 1

    base_url = ready["host"]
    prompt_id = submit_prompt(base_url, config, workflow)
    images = wait_for_images(base_url, config, prompt_id)

    output_dir = Path(config["paths"]["workspace_output_dir"])
    downloaded = [download_image(base_url, config, image, output_dir) for image in images]

    print(
        json.dumps(
            {
                "ok": True,
                "workflow": "HadrianXL3.0",
                "prompt_id": prompt_id,
                "seed": seed,
                "host": base_url,
                "files": downloaded,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
