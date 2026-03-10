#!/usr/bin/env python3
"""Reserved workflow entry for image_z_image_turbo."""

from __future__ import annotations

import json


def main() -> int:
    print(
        json.dumps(
            {
                "ok": False,
                "workflow": "image_z_image_turbo",
                "status": "not_implemented",
                "message": "This workflow needs its own image-input generate implementation before use.",
            },
            ensure_ascii=False,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
