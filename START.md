# START

This file is a temporary startup guide.

When OpenClaw first takes over this skill, or local paths are not confirmed yet, read this first.
After local path setup is finished and the workflow source is confirmed, this file can be deleted.

## Goal

Use this skill as a general local ComfyUI skill:

1. ask the user for local paths first
2. ask which workflow the user wants
3. find that workflow inside the user's own ComfyUI directory
4. create the workflow folder under `workflows/`
5. write the workflow-specific `_generate.py`
6. run `--dry-run`, then do one safe real test

## Step 1: ask for local paths first

Do not guess paths first. Ask the user and record:

- ComfyUI root directory
- ComfyUI workflow source directory
- which ComfyUI instance owns models and outputs
- where this skill is currently stored

At minimum, confirm:

- `ComfyUI root`
- `ComfyUI workflow source dir`

If the user has not given a full path yet, keep asking until the actual workflow files can be found.

## Step 2: ask which workflow the user wants

After paths are confirmed, do not pick a workflow on your own.

Ask the user:

- which workflow to use
- whether to run an existing workflow or adapt a new one

Only after the workflow is explicitly specified should you continue.

## Step 3: find the workflow in the user's ComfyUI directory

This repository does not provide a universal `_generate.py` library or a universal workflow registry.

Correct flow:

1. go to the user's own ComfyUI workflow directory
2. find the target `.json`
3. copy it into:

```text
workflows/<workflow-name>/<workflow-name>.json
```

If the workflow is new to this skill, create the folder first.

## Step 4: create the three-file workflow folder

Each workflow uses this fixed layout:

```text
workflows/<workflow-name>/
  <workflow-name>.json
  <workflow-name>_generate.py
  workflow.md
```

Meaning:

- `.json`: raw workflow copied from the user's ComfyUI workflow directory
- `_generate.py`: workflow-specific generator written by OpenClaw
- `workflow.md`: parameter meanings, node notes, minimal usage

## Step 5: `_generate.py` is not a prebuilt repository feature

Rule:

- the repository provides shared layers and a few examples
- new workflows get their own `_generate.py` written on demand

Do not assume the repository already contains a generator for every workflow.

## Step 6: always do a safe test first

After writing `_generate.py`, always do:

1. `--dry-run`
2. one safe, short, visible-prompt real generation

Do not start with a complex task.

## Execution rules

- paths first, workflow second
- ask which workflow first, then find its source file
- create the folder before writing `_generate.py`
- dry-run before real run
- do not scan the whole disk by default
- do not choose a workflow on your own

## Related docs

- main entry: `SKILL.md`
- structure notes: `LEARNING.md`
- generator writing guide: `GENERATE_MANUAL.md`
