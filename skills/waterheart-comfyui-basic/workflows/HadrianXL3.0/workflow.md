# HadrianXL3.0

绑定文件：

- `HadrianXL3.0.json`
- `HadrianXL3.0_generate.py`

当前支持参数：

- `--prompt`
作用：追加到节点 `51` 的正向正文提示词后面

- `--seed`
作用：写入节点 `31.inputs.seed`

- `--dry-run`
作用：只验证 prompt 和 seed 注入，不提交 ComfyUI

推荐命令：

```bash
python3 skills/waterheart-comfyui-basic/workflows/HadrianXL3.0/HadrianXL3.0_generate.py --prompt "a cute anime cat"
```
