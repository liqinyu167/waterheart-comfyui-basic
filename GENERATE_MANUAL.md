# Generate Script Manual

这份手册只讲一件事：
怎么给 `waterheart-comfyui-basic` 新增一个 workflow 专属生成器。

## 目录规则

当前固定目录结构：

```text
skills/waterheart-comfyui-basic/
  scripts/
    comfy_manager.py
    comfy_deliver.py
  workflows/
    <workflow-name>/
      <workflow-name>.json
      <workflow-name>_generate.py
      workflow.md
```

含义：

- `workflows/<name>/`：已经正式接入 skill 的 workflow

## 标准流程

新增一个 workflow 时，固定按下面 6 步走：

1. 先让用户提供 ComfyUI workflow 源目录
2. 再让用户指定这次要适配哪个 workflow
3. 把原始 workflow JSON 复制到 `workflows/<name>/`
4. 从原始 workflow 分析节点关系
5. 和用户确认哪些参数做成可变参数，哪些保持固定
6. 写 `<name>_generate.py` 和 `workflow.md`

不要一上来就直接写生成器。先把节点关系盘清楚。

节点说明直接写进：

- `<workflow-name>_generate.py`
- `workflow.md`

原则是：先和用户确认“哪些参数可变、哪些固定”，再写代码。

workflow 来源原则：

- 先找用户自己 ComfyUI 目录里的 workflow
- 不要默认扫描无关目录
- 不要先从仓库假设 workflow 存在

## 先跟用户确认什么

在写专属 `generate.py` 前，先确认这几个点：

- 哪些参数开放给用户改，例如 `prompt`、`seed`、`image`
- 哪些参数保持固定，例如 `steps`、`cfg`、`sampler`、`size`
- 这个 workflow 是单图还是多图
- 输出是图片、编辑结果，还是别的格式

不要为了“做全”把所有节点都暴露成参数。

默认原则：

- 用户明确会经常改的，做成参数
- 只为这个 workflow 服务、平时不改的，写死在脚本里

## 什么时候需要专属 generate.py

只要这个 workflow 不是“和现有 workflow 完全同类”，就直接写专属脚本。

适合专属脚本的情况：

- 节点结构明显不同
- 需要输入图片
- 需要 mask 或参考图
- 需要多个 prompt
- 需要单独注入 seed / batch / width / height
- 输出不是标准 image 列表

原则：

- 一个 workflow，一个生成脚本
- 不要让一个脚本去猜多个 workflow

## 正式接入后的目录

正式接入后，统一整理成：

```text
workflows/MyWorkflow/
  MyWorkflow.json
  MyWorkflow_generate.py
  workflow.md
```

## generate.py 的最小结构

一个可维护的 workflow 专属脚本，只保留 6 段：

### 1. 常量区

写死这个 workflow 自己的路径、节点号和必要字段名。

```python
WORKFLOW_PATH = Path(__file__).resolve().with_name("MyWorkflow.json")
PROMPT_NODE = "51"
PROMPT_FIELD = "string"
SEED_NODE = "31"
```

不要把别的 workflow 的节点混进来。

### 2. 读取 workflow

```python
def read_workflow() -> dict:
    return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
```

每次运行都重新读取，不要复用上一轮改过的对象。

### 3. 参数注入

按这个 workflow 自己的节点改值。

```python
def inject_prompt(workflow: dict, visible_prompt: str) -> str:
    node = workflow[PROMPT_NODE]
    existing = node.setdefault("inputs", {}).get(PROMPT_FIELD, "")
    final_prompt = f"{existing}, {visible_prompt}".strip(", ")
    node["inputs"][PROMPT_FIELD] = final_prompt
    return final_prompt
```

```python
def inject_seed(workflow: dict, seed: int) -> None:
    workflow[SEED_NODE]["inputs"]["seed"] = seed
```

以后如果是 img2img，再新增：

- `inject_input_image()`
- `inject_mask()`
- `inject_size()`

### 4. 提交任务

共用 ComfyUI API，不要自己发明协议。

```python
def submit_prompt(base_url: str, workflow: dict) -> str:
    response = requests.post(f"{base_url}/prompt", json={"prompt": workflow}, timeout=30)
    response.raise_for_status()
    return response.json()["prompt_id"]
```

### 5. 等输出

默认图像 workflow 看 `history/{prompt_id}` 里的 `outputs.images`。

不要只看“任务提交成功”，也不要只看“history 里有记录”，必须等真的有实际输出。

如果不是标准图片 workflow，就按这个 workflow 的真实输出字段实现等待逻辑。

### 6. 下载输出

把结果拉回：

```text
/home/qinyu/.openclaw/workspace-shuixin/outputs
```

这样后面的交付链不用改。

## 主流程模板

```python
def main() -> int:
    args = parse_args()
    config = load_config()
    workflow = read_workflow()

    seed = normalize_seed(args.seed)
    final_prompt = inject_prompt(workflow, args.prompt)
    inject_seed(workflow, seed)

    if args.dry_run:
        print(...)
        return 0

    ready = ensure_ready(config)
    if not ready.get("ok"):
        print(...)
        return 1

    prompt_id = submit_prompt(ready["host"], workflow)
    images = wait_for_images(ready["host"], config, prompt_id)
    files = download_outputs(...)
    print(...)
    return 0
```

## 参数设计原则

只暴露这个 workflow 真正支持的参数。

例如一个最小 txt2img workflow，可能只暴露：

- `--prompt`
- `--seed`
- `--dry-run`

不要为了“统一”把根本没接上的参数也暴露出来，例如：

- `--negative`
- `--width`
- `--height`
- `--batch`
- `--image`

脚本没处理，就不要加。

## dry-run 必须有

每个 generate 脚本都应该支持：

```text
--dry-run
```

作用：

- 不提交 ComfyUI
- 只检查 workflow 能不能读
- 只检查节点能不能改
- 打印最终 prompt / seed / workflow 名

这样能在不跑 GPU 的情况下先确认逻辑没写错。

## workflow.md 怎么写

每个 workflow 目录里的 `workflow.md` 建议固定模板：

````md
# MyWorkflow

绑定文件：
- MyWorkflow.json
- MyWorkflow_generate.py

支持参数：
- --prompt: 写到哪个节点
- --seed: 写到哪个节点
- --dry-run: 做什么

最小调用命令：
```bash
python3 skills/waterheart-comfyui-basic/workflows/MyWorkflow/MyWorkflow_generate.py --prompt "test"
```
````

## 常见错误

### 错误 1：节点号照抄别的 workflow

症状：

- 提交成功
- 但 `Prompt executed in 0.00 seconds`
- 或没有图片输出

原因：

- prompt/seed 根本没写到真正的节点

### 错误 2：复用改过的 workflow 对象

症状：

- 第一张能跑
- 第二张开始异常

原因：

- 不是每次都从磁盘重新读取 JSON

### 错误 3：只等 history，不等图片

症状：

- 返回 0 张
- 或任务看起来完成，但没下载到文件

原因：

- 过早把 history 当成完成信号

### 错误 4：把通用逻辑复制进每个脚本

不要在每个 workflow 专属脚本里重复写：

- Windows host 发现逻辑
- 启动 ComfyUI 逻辑
- 飞书交付逻辑

这些继续共用：

- `scripts/comfy_manager.py`
- `scripts/comfy_deliver.py`
