#!/usr/bin/env python3
"""校验 tasks.md 的每一项任务都追溯到 requirements.md 里真实存在的需求编号。

用法：python3 check_trace.py <spec目录>
退出码：0 = 全部可追溯；1 = 发现问题。

规则：
1. 每条任务（以 "- [ ]" 或 "- [x]" 开头的编号行）后面必须跟一行 "_需求: Rx.y, ..._"。
2. 任务引用的每个需求编号必须在 requirements.md 中定义过。
3. requirements.md 中定义的每个需求都至少被一条任务覆盖（反向追溯）。
"""
import re
import sys
from pathlib import Path

REQ_DEF = re.compile(r"\b(R\d+\.\d+)\b")           # 需求定义：R1.1
TASK_LINE = re.compile(r"^- \[[ x]\]\s+(\d+)\.\s+(.*)")  # 任务行：- [ ] 1. xxx
TRACE_LINE = re.compile(r"_需求:\s*([^_]+)_")       # 追溯行：_需求: R1.1, R3.1_


def load_requirement_ids(req_path: Path) -> set[str]:
    """从 requirements.md 的「验收标准（EARS）」条目里收集所有 Rx.y 编号。"""
    ids = set()
    for line in req_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        # 只认验收标准条目（以 "- Rx.y" 开头），不认标题里的偶然匹配
        if s.startswith("- R"):
            m = REQ_DEF.match(s[2:].strip())
            if m:
                ids.add(m.group(1))
    return ids


def load_tasks(tasks_path: Path):
    """返回 [(任务号, 标题, [引用的需求ID...])]；没有追溯行的记为 None。"""
    lines = tasks_path.read_text(encoding="utf-8").splitlines()
    tasks = []
    i = 0
    while i < len(lines):
        m = TASK_LINE.match(lines[i])
        if m:
            num, title = m.group(1), m.group(2).strip()
            refs = None
            # 向后看几行找追溯标签
            for j in range(i + 1, min(i + 4, len(lines))):
                t = TRACE_LINE.search(lines[j])
                if t:
                    refs = REQ_DEF.findall(t.group(1))
                    break
                if TASK_LINE.match(lines[j]):
                    break
            tasks.append((num, title, refs))
        i += 1
    return tasks


def main() -> int:
    if len(sys.argv) != 2:
        print("用法：python3 check_trace.py <spec目录>")
        return 2
    spec = Path(sys.argv[1])
    req_path = spec / "requirements.md"
    tasks_path = spec / "tasks.md"
    if not req_path.exists() or not tasks_path.exists():
        print(f"找不到 {req_path} 或 {tasks_path}")
        return 2

    req_ids = load_requirement_ids(req_path)
    tasks = load_tasks(tasks_path)

    problems = []
    covered = set()
    for num, title, refs in tasks:
        if refs is None:
            problems.append(f"任务 {num}「{title}」缺少 _需求:_ 追溯标签")
            continue
        for r in refs:
            if r not in req_ids:
                problems.append(f"任务 {num} 引用了不存在的需求 {r}")
            else:
                covered.add(r)

    # 反向追溯：有需求没被任何任务覆盖
    orphan = req_ids - covered
    for r in sorted(orphan):
        problems.append(f"需求 {r} 没有任何任务覆盖")

    print(f"需求数：{len(req_ids)}  任务数：{len(tasks)}  已覆盖需求：{len(covered)}")
    if problems:
        print("FAIL：发现追溯问题")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("PASS：每条任务都追溯到真实需求，且每个需求都被覆盖")
    return 0


if __name__ == "__main__":
    sys.exit(main())
