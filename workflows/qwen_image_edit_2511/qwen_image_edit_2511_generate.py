#!/usr/bin/env python3
"""Reserved workflow entry for qwen_image_edit_2511."""

from __future__ import annotations

import json


def main() -> int:
    print(
        json.dumps(
            {
                "ok": False,
                "workflow": "qwen_image_edit_2511",
                "status": "not_implemented",
                "message": "This workflow needs its own image-edit generate implementation before use.",
            },
            ensure_ascii=False,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
