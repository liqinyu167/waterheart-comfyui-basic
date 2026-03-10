# waterheart-comfyui-basic

`waterheart-comfyui-basic` 是一个给 OpenClaw 用的本地 ComfyUI skill。

它的定位不是通用图形前端，而是一个让 OpenClaw 能稳定接管本机 ComfyUI 的执行型 skill。
这个项目当前代码和文档内容绝大部分由 AI 协作生成，可以近似理解为“99% AI 代码含量”的实验型自动化 skill。

核心思路很简单：

- `Windows` 侧运行 ComfyUI 和模型
- `WSL` 侧运行 skill 脚本
- `WSL` 通过 HTTP API 连接 `Windows` 上的 ComfyUI

也就是：

```text
WSL skill -> Windows ComfyUI API -> Windows GPU 推理
```

## 这个 skill 是做什么的

这个项目用于：

- 启动和检查本机 ComfyUI
- 通过 WSL 调用 Windows 侧 ComfyUI API
- 为指定 workflow（API格式workflow） 编写专属 `_generate.py`
- 测试生成
- 生成后准备飞书附件交付

## 第一次配置怎么做

第一次接手时，先看：

- `START.md`

然后确认这些本机信息：

1. `ComfyUI root`
2. `ComfyUI workflow source dir`
3. 当前 OpenClaw workspace 路径
4. 飞书 inbound 目录
5. Windows 计划任务名是否正确

项目里的共享配置在：

- `config.json`

至少要检查这些字段：

- `comfy.task_name`
- `paths.workspace_root`
- `paths.workspace_output_dir`
- `paths.workflow_root_dir`
- `paths.media_inbound_dir`

## 当前默认启动项

当前项目默认通过 Windows 计划任务启动 ComfyUI：

- `ComfyUI-AKI`

当前默认假设的启动方向是：

- 由 `scripts/comfy_manager.py` 调用计划任务
- ComfyUI 必须对 WSL 可访问
- WSL 不直接起一套自己的 ComfyUI

如果你的本机启动方式不同，就要先改 `config.json` 和本地计划任务。

## 网络连接说明

这套 skill 的关键点不是 `WSL -> 127.0.0.1:8188`，而是：

- `WSL` 通过 Windows 主机 IP 访问 ComfyUI

默认规则：

- 不要在 WSL 里用 `127.0.0.1:8188`
- ComfyUI 需要开启 `--listen`
- WSL 通过默认网关解析 Windows 主机地址

如果 ComfyUI 只绑定在 Windows 的本地回环地址，WSL 就会连不上。

## 当前功能

目前项目里已经有：

- `scripts/comfy_manager.py`
  负责启动、状态检查、主机发现

- `scripts/comfy_deliver.py`
  负责准备飞书附件发送参数

- `workflows/HadrianXL3.0/`
  当前完整示例 workflow

- `workflows/image_z_image_turbo/`
  预留目录，等待专属生成器

- `workflows/qwen_image_edit_2511/`
  预留目录，等待专属生成器

## 当前推荐流程

1. 先读 `START.md`
2. 让用户提供本机 ComfyUI 路径
3. 让用户指定要用哪个 workflow
4. 把 workflow 放进 `workflows/<workflow-name>/`
5. 写 `<workflow-name>_generate.py`
6. 先跑 `--dry-run`
7. 再跑一次安全测试生成

## 当前示例

`HadrianXL3.0` 是现在的完整示例。

当前支持：

- 可见 prompt
- 随机或固定 seed
- `--dry-run`

其他 workflow 目前还不是完整实现，而是为后续适配预留的目录。
