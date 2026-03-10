# Waterheart ComfyUI Basic - Learning Notes

这份文档只解释新的目录法。

## 1. 统一目录结构

每个 workflow 固定一个目录：

```text
workflows/<workflow-name>/
  <workflow-name>.json
  <workflow-name>_generate.py
  workflow.md
```

例子：

```text
workflows/HadrianXL3.0/
  HadrianXL3.0.json
  HadrianXL3.0_generate.py
  workflow.md
```

## 2. 通用层只保留两个脚本

- [comfy_manager.py](/home/qinyu/.openclaw/workspace-shuixin/skills/waterheart-comfyui-basic/scripts/comfy_manager.py)
- [comfy_deliver.py](/home/qinyu/.openclaw/workspace-shuixin/skills/waterheart-comfyui-basic/scripts/comfy_deliver.py)

意思是：

- 启动和状态检查共用
- 飞书交付准备共用
- 生成逻辑不再共用

## 3. 每个 generate 脚本只绑定自己的 workflow

例子：

- [HadrianXL3.0_generate.py](/home/qinyu/.openclaw/workspace-shuixin/skills/waterheart-comfyui-basic/workflows/HadrianXL3.0/HadrianXL3.0_generate.py)
只绑定：
- [HadrianXL3.0.json](/home/qinyu/.openclaw/workspace-shuixin/skills/waterheart-comfyui-basic/workflows/HadrianXL3.0/HadrianXL3.0.json)

不要让一个通用生成器去猜多个 workflow。

## 4. workflow.md 该写什么

每个 `workflow.md` 只写：

1. 绑定哪个 json
2. 绑定哪个 generate 脚本
3. 支持哪些参数
4. 每个参数写进哪个节点
5. 最小调用命令

## 5. 什么时候加新 workflow

步骤固定：

1. 新建目录 `workflows/<workflow-name>/`
2. 放入 `<workflow-name>.json`
3. 新建 `<workflow-name>_generate.py`
4. 新建 `workflow.md`
5. 跑 `--dry-run`
6. 跑一次真实安全 prompt

## 6. Hadrian 当前支持什么

当前 Hadrian 只支持：

- `--prompt`
- `--seed`
- `--dry-run`

当前真正可用入口是：

```bash
python3 skills/waterheart-comfyui-basic/workflows/HadrianXL3.0/HadrianXL3.0_generate.py --prompt "a cute anime cat"
```

## 7. 其他 workflow 当前状态

- `image_z_image_turbo`：只有骨架，未实现
- `qwen_image_edit_2511`：只有骨架，未实现

这样做的目的不是拖慢，而是避免把不同类型的 workflow 混进一份脚本。

## 8. 通用配置只保留公共项

[config.json](/home/qinyu/.openclaw/workspace-shuixin/skills/waterheart-comfyui-basic/config.json) 现在只保留：

- ComfyUI API 参数
- Windows 计划任务名
- workspace 输出目录
- workflow 根目录
- 飞书 inbound 目录
- 默认飞书目标

不再在这里维护 workflow profile。
