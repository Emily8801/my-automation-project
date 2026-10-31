"""模型输出落盘：解析 Stage C 的 # FILE: 协议输出，拆分写入目标目录

Stage C 提示词约定了输出协议（见 prompts/stage_c_generate.md）：
  # FILE: pages/login_page.py
  ```python
  <代码>
  ```
本模块负责按该协议解析并写文件。
"""
import re
from pathlib import Path

# 匹配 "# FILE: 相对路径" 标题行
FILE_HEADER = re.compile(r"^#\s*FILE:\s*(\S+)\s*$", re.MULTILINE)
# 匹配 ```python ... ``` 代码块
CODE_BLOCK = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)


def split_files(model_output: str) -> dict[str, str]:
    """把模型输出拆成 {相对路径: 文件内容} 的字典

    每个 '# FILE: xxx' 标题后的第一个 python 代码块，即为该文件的内容。
    """
    files: dict[str, str] = {}
    headers = list(FILE_HEADER.finditer(model_output))
    for i, header in enumerate(headers):
        path = header.group(1)
        # 该标题到下一段标题之间的文本，找第一个 python 代码块
        end = headers[i + 1].start() if i + 1 < len(headers) else len(model_output)
        block = CODE_BLOCK.search(model_output, header.end(), end)
        if block:
            files[path] = block.group(1).rstrip() + "\n"
    return files


def write_files(files: dict[str, str], project_dir: str | Path) -> list[Path]:
    """把拆分出的文件写入 project_dir，返回实际写入的路径列表"""
    root = Path(project_dir)
    written = []
    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written
