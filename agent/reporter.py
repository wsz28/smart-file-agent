"""
reporter.py
生成 Markdown 整理报告，并负责全过程日志写入。
"""
import os
import time
from pathlib import Path


class Reporter:
    def __init__(self, log_path: str = None):
        self.log_path = log_path
        self.entries = []          # 记录 (src_name, category, level, dst, moved)
        if log_path:
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n=== 运行 {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    def log(self, msg: str):
        if self.log_path:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        print(msg)

    def add(self, src_name, category, level, dst, moved):
        self.entries.append({
            "name": src_name, "category": category,
            "level": level, "dst": dst, "moved": moved,
        })

    def write_markdown(self, out_path: str) -> None:
        """生成 Markdown 整理报告。"""
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        lines = []
        lines.append("# 文件整理报告")
        lines.append(f"\n生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n共处理 **{len(self.entries)}** 个文件。\n")
        # 按分类统计
        from collections import Counter
        cnt = Counter(e["category"] for e in self.entries)
        lines.append("## 分类统计")
        for cat, n in cnt.most_common():
            lines.append(f"- **{cat}**：{n}")
        # 明细
        lines.append("\n## 明细")
        lines.append("\n| 文件名 | 分类 | 命中方式 | 目标 | 已移动 |")
        lines.append("|---|---|---|---|---|")
        for e in self.entries:
            moved = "是" if e["moved"] else "否"
            lines.append(f"| {e['name']} | {e['category']} | {e['level']} | `{e['dst']}` | {moved} |")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[报告] 已写入 {out_path}")
