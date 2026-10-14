"""
mover.py
归档模块：把文件移动到分类目录。
安全设计：默认 dry-run 只预览不操作；只移动不删除；重名自动加序号。
"""
import os
import shutil
from pathlib import Path


def _unique_path(target: Path) -> Path:
    """若目标已存在，自动追加 (1)(2)... 序号，避免覆盖。"""
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 1
    while True:
        cand = target.with_name(f"{stem} ({i}){suffix}")
        if not cand.exists():
            return cand
        i += 1


def plan_moves(files, rules, dest_root: str):
    """生成移动计划：[(src, dst), ...]，按分类目录组织。"""
    plan = []
    dest_root = Path(dest_root)
    default = rules["default_category"]
    categories = rules["categories"]
    # 临时用扩展名规则做预分类（正式分类由 run.py 传入，这里兼容直接调用）
    for fpath in files:
        cat = default
        ext = fpath.suffix.lower()
        for c in categories:
            if ext in c.get("extensions", []):
                cat = c["name"]
                break
        plan.append((fpath, dest_root / cat / fpath.name))
    return plan


def apply_move(src: Path, dst: Path, dry_run: bool, log_fn=None):
    """执行移动。dry_run=True 时仅记录不操作。返回最终目标路径。"""
    dst_final = _unique_path(dst) if not dry_run else dst
    if log_fn:
        log_fn(f"{'[DRY]' if dry_run else '[MOVE]'} {src.name} -> {dst_final.relative_to(Path.cwd())}")
    if not dry_run:
        dst_final.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst_final))
    return dst_final


def build_dest_tree(dest_root: str, rules: dict) -> None:
    """预创建所有分类目录。"""
    root = Path(dest_root)
    root.mkdir(parents=True, exist_ok=True)
    for cat in rules["categories"]:
        (root / cat["name"]).mkdir(parents=True, exist_ok=True)
    (root / rules["default_category"]).mkdir(parents=True, exist_ok=True)
