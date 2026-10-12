#!/usr/bin/env python3
"""Demo 2-1：同一组 commit，按不同口径算"AI 写了多少"，得出不同结论。

本脚本不依赖任何第三方库，内置一小批"半虚构"的 commit 记录
（技术细节真实可跑，数据为本书构造的示意数据）。
每条 commit 记录包含：
  - author：commit 作者标记（"ai" / "human"）
  - added / deleted：本次提交净增 / 删除的代码行
  - ai_suggested：AI 当时"吐出来"的行数（可能大于最终 added——被人改掉或删掉）
  - ai_kept：AI 吐出的行里，最终真正留在代码库里的行数
  - kind：feature / refactor / fixup（用于演示"重构不该算 AI 产量"等口径）

然后用 5 种常见口径分别计算"AI 写了百分之多少"，
展示：同一批数据，口径不同，结论从 38% 到 86% 不等。
"""

# 本书构造案例 · 示意数据（10 条 commit）
COMMITS = [
    # author,   added, deleted, ai_suggested, ai_kept, kind
    {"author": "ai",    "added": 120, "deleted": 10,  "ai_suggested": 200, "ai_kept": 120, "kind": "feature"},
    {"author": "ai",    "added": 300, "deleted": 0,   "ai_suggested": 520, "ai_kept": 300, "kind": "feature"},
    {"author": "human", "added": 40,  "deleted": 5,   "ai_suggested": 15,  "ai_kept": 12,  "kind": "feature"},
    {"author": "ai",    "added": 60,  "deleted": 200, "ai_suggested": 60,  "ai_kept": 60,  "kind": "refactor"},
    {"author": "human", "added": 25,  "deleted": 3,   "ai_suggested": 0,   "ai_kept": 0,   "kind": "fixup"},
    {"author": "ai",    "added": 180, "deleted": 20,  "ai_suggested": 420, "ai_kept": 180, "kind": "feature"},
    {"author": "human", "added": 90,  "deleted": 10,  "ai_suggested": 50,  "ai_kept": 30,  "kind": "feature"},
    {"author": "ai",    "added": 15,  "deleted": 0,   "ai_suggested": 15,  "ai_kept": 15,  "kind": "fixup"},
    {"author": "human", "added": 50,  "deleted": 40,  "ai_suggested": 0,   "ai_kept": 0,   "kind": "refactor"},
    {"author": "ai",    "added": 70,  "deleted": 5,   "ai_suggested": 130, "ai_kept": 70,  "kind": "feature"},
]


def pct(num, den):
    return 0.0 if den == 0 else round(100.0 * num / den, 1)


def by_commit_count(commits):
    """口径①：按提交数——作者标为 ai 的 commit 占全部 commit 的比例。"""
    ai = sum(1 for c in commits if c["author"] == "ai")
    return pct(ai, len(commits))


def by_added_lines_author(commits):
    """口径②：按新增行数——ai 作者的 commit 新增的行，占全部新增行的比例。"""
    ai = sum(c["added"] for c in commits if c["author"] == "ai")
    total = sum(c["added"] for c in commits)
    return pct(ai, total)


def by_ai_suggested(commits):
    """口径③：按 AI "吐出来"的行数——AI 建议过的行，占"全部新增 + AI 建议"的比例。
    这是把"AI 吐出但被推翻"的行也算成 AI 产量的灌水口径。"""
    suggested = sum(c["ai_suggested"] for c in commits)
    human_added = sum(c["added"] for c in commits if c["author"] == "human")
    return pct(suggested, suggested + human_added)


def by_ai_kept(commits):
    """口径④：按 AI "留下来"的行数——AI 吐出且最终保留的行，占全部新增行的比例。
    对照 METR"接受率不到 44%"：吐出 ≠ 留下。"""
    kept = sum(c["ai_kept"] for c in commits)
    total = sum(c["added"] for c in commits)
    return pct(kept, total)


def by_added_excluding_refactor(commits):
    """口径⑤：按新增行数、但剔除重构——重构是"把代码变少变清晰"，
    不该算进"写了多少新代码"。只在 feature/fixup 里算 AI 新增占比。"""
    pool = [c for c in commits if c["kind"] != "refactor"]
    ai = sum(c["added"] for c in pool if c["author"] == "ai")
    total = sum(c["added"] for c in pool)
    return pct(ai, total)


def main():
    rows = [
        ("① 按提交数（commit 占比）",            by_commit_count(COMMITS)),
        ("② 按新增行数（作者=ai 的新增行占比）",  by_added_lines_author(COMMITS)),
        ("③ 按 AI 吐出的行（含被推翻的）",        by_ai_suggested(COMMITS)),
        ("④ 按 AI 留下的行（吐出≠留下）",         by_ai_kept(COMMITS)),
        ("⑤ 按新增行、剔除重构",                  by_added_excluding_refactor(COMMITS)),
    ]
    print("同一组 10 条 commit，5 种口径算\"AI 写了多少\"：")
    print("-" * 46)
    for name, value in rows:
        bar = "#" * int(value / 2)
        print(f"{name:<30} {value:>5.1f}%  {bar}")
    print("-" * 46)
    vals = [v for _, v in rows]
    print(f"最低 {min(vals):.1f}%  最高 {max(vals):.1f}%  极差 {max(vals) - min(vals):.1f} 个百分点")
    print("结论：没有统一口径时，\"AI 写了多少\"这句话本身没有意义。")


if __name__ == "__main__":
    main()
