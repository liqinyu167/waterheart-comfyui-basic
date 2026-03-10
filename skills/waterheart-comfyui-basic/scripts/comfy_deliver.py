#!/usr/bin/env python3
"""Prepare a generated image for Feishu attachment delivery."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from comfy_manager import load_config

SOURCE_DEFAULT = "白刀（主助理转达）"
LINE_FROM = "指令来自："
LINE_SUMMARY = "发出去的内容："
LINE_FILE = "交付物："


def stage_file(src_path: Path, inbound_dir: Path) -> Path:
    inbound_dir.mkdir(parents=True, exist_ok=True)
    dst_path = inbound_dir / src_path.name
    shutil.copy2(src_path, dst_path)
    return dst_path


def build_caption(source: str, summary: str, filename: str) -> str:
    return "\n".join(
        [
            f"{LINE_FROM}{source}",
            f"{LINE_SUMMARY}{summary}",
            f"{LINE_FILE}{filename}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Feishu attachment delivery payload.")
    parser.add_argument("--file", required=True, help="Generated image path")
    parser.add_argument("--source", default=SOURCE_DEFAULT, help="Who issued the instruction")
    parser.add_argument("--summary", required=True, help="Short one-line description of the delivered content")
    parser.add_argument("--target", default=None, help="Feishu open_id override")
    args = parser.parse_args()

    config = load_config()
    src_path = Path(args.file).expanduser().resolve()
    if not src_path.exists():
        raise FileNotFoundError(f"Generated file not found: {src_path}")

    inbound_dir = Path(config["paths"]["media_inbound_dir"])
    staged = stage_file(src_path, inbound_dir)
    target = args.target or config["defaults"]["feishu_target"]
    caption = build_caption(args.source, args.summary, staged.name)

    print(
        json.dumps(
            {
                "ok": True,
                "target": target,
                "file_path": str(staged),
                "caption": caption,
                "message_tool": {
                    "action": "send",
                    "filePath": str(staged),
                    "caption": caption,
                    "target": target,
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
