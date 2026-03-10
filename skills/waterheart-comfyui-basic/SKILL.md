---
name: waterheart-comfyui-basic
description: Use this skill for Waterheart local ComfyUI work on the current machine. Each workflow lives under workflows/<name>/ with its own generate script, json, and md.
---

# Waterheart ComfyUI Basic

This is Waterheart's only local ComfyUI skill.

## Execute Only

### 1. Start or check ComfyUI

```bash
python3 skills/waterheart-comfyui-basic/scripts/comfy_manager.py ensure-ready
python3 skills/waterheart-comfyui-basic/scripts/comfy_manager.py status
```

### 2. Generate

Current default workflow:

```bash
python3 skills/waterheart-comfyui-basic/workflows/HadrianXL3.0/HadrianXL3.0_generate.py --prompt "a cute anime cat"
python3 skills/waterheart-comfyui-basic/workflows/HadrianXL3.0/HadrianXL3.0_generate.py --prompt "a cute anime cat" --seed 123456789
```

### 3. Prepare Feishu attachment delivery

```bash
python3 skills/waterheart-comfyui-basic/scripts/comfy_deliver.py --file /home/qinyu/.openclaw/workspace-shuixin/outputs/ComfyUI_temp_xxx.png --summary "a cute anime cat"
```

Then use the message tool with:

- `target`
- `filePath`
- `caption`

from the JSON output of `comfy_deliver.py`.

## Structure

Every workflow must use this layout:

```text
workflows/<workflow-name>/
  <workflow-name>.json
  <workflow-name>_generate.py
  workflow.md
```

Current directories:

- `workflows/HadrianXL3.0/`
- `workflows/image_z_image_turbo/`
- `workflows/qwen_image_edit_2511/`

## Current Boundaries

- visible prompt only for Hadrian
- optional seed only for Hadrian
- single image per run
- default Feishu target: `ou_b995b8c07067086cfe0fb816ad4aeef3`
- scheduled task: `ComfyUI-AKI`

## Do Not Do

- do not use deleted or legacy ComfyUI skills
- do not use `127.0.0.1:8188` from WSL
- do not scan the Windows workflow library by default
- do not create hidden prompt txt files
- do not read private prompt content
- do not inspect generated images by default

## Learn More

Detailed extension notes stay in:

- `LEARNING.md`
- when creating or adapting a workflow-specific generator, also read `GENERATE_MANUAL.md`
