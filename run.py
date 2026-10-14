"""
run.py
智能文件整理 Agent 主入口。

流程：扫描 → 三级分类决策 → 归档（默认 dry-run）→ 报告

用法示例：
  python run.py --src ./downloads                     # 默认 dry-run，仅预览
  python run.py --src ./downloads --apply             # 真正执行移动
  python run.py --src ./downloads --apply --llm       # 开启可选大模型裁决
  python run.py --src ./downloads --dest ./sorted --rules rules.json --log agent.log
"""
import argparse
import os
from pathlib import Path

from agent import scanner, classifier, mover, reporter


def parse_args():
    p = argparse.ArgumentParser(description="智能文件整理 Agent")
    p.add_argument("--src", default="downloads", help="待整理的源目录")
    p.add_argument("--dest", default="sorted", help="归档目标根目录")
    p.add_argument("--rules", default="rules.json", help="分类规则 JSON 路径")
    p.add_argument("--log", default="agent.log", help="日志文件路径")
    p.add_argument("--report", default="report.md", help="Markdown 报告输出路径")
    p.add_argument("--apply", action="store_true", help="真正移动文件（默认 dry-run 只预览）")
    p.add_argument("--llm", action="store_true", help="启用可选大模型裁决（需 LLM_API_KEY）")
    return p.parse_args()


def main():
    args = parse_args()

    rules = classifier.load_rules(args.rules)
    rep = reporter.Reporter(args.log)

    rep.log(f"[INFO] 源目录: {args.src} | 目标: {args.dest} | 模式: {'APPLY' if args.apply else 'DRY-RUN'}")
    if args.llm and not classifier.llm.enabled():
        rep.log("[WARN] 未设置 LLM_API_KEY，大模型裁决已跳过，回落扩展名/默认规则")

    files = scanner.collect(args.src, rules)
    rep.log(f"[INFO] 扫描到 {len(files)} 个待整理文件")

    mover.build_dest_tree(args.dest, rules)

    moved_count = 0
    for fpath in files:
        cat, level = classifier.classify_file(
            fpath, rules["categories"], rules["default_category"], use_llm=args.llm
        )
        dst = Path(args.dest) / cat / fpath.name
        moved = not args.apply
        final_dst = mover.apply_move(
            fpath, dst, dry_run=not args.apply, log_fn=rep.log
        )
        if args.apply:
            moved = True
        rep.add(fpath.name, cat, level, str(final_dst), moved)
        if args.apply:
            moved_count += 1

    rep.write_markdown(args.report)
    rep.log(f"[DONE] 共处理 {len(files)} 个文件，实际移动 {moved_count} 个。报告: {args.report}")


if __name__ == "__main__":
    main()
