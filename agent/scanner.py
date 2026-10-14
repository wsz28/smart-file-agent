"""
scanner.py
扫描目标目录，收集待整理的文件。
只处理普通文件，跳过目录、隐藏系统文件与预设"垃圾"文件。
"""
import os
from pathlib import Path


def iter_files(root: str, rules: dict, skip_dirs=("node_modules", ".git", ".venv", "__pycache__")):
    """递归遍历 root，产出待整理的文件路径。"""
    root = Path(root)
    trash = set(rules.get("trash", []))
    for dirpath, dirnames, filenames in os.walk(root):
        # 就地裁剪，避免进入跳过目录
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            # 跳过隐藏文件与垃圾文件
            if fname.startswith("."):
                continue
            if fname in trash:
                continue
            yield fpath


def collect(root: str, rules: dict):
    """返回待整理文件列表。"""
    files = list(iter_files(root, rules))
    return files
