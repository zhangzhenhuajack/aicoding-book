import json, sys

SEVERITIES = {"P0", "P1", "P2"}            # 允许的严重性档位
MIN_EVIDENCE = 10                          # 证据至少 10 字符,挡掉"有问题"式空话
ACTION_HINTS = ("改", "用", "加", "删", "拆", "换", "补", "应",
                "use", "add", "replace", "extract", "split", "remove", "wrap")

def lint_comment(c):
    problems = []
    if c.get("severity") not in SEVERITIES:
        problems.append(f"severity 非法或缺失: {c.get('severity')!r}")
    ev = (c.get("evidence") or "").strip()
    if len(ev) < MIN_EVIDENCE:
        problems.append("证据不足(evidence 太短)")
    if c.get("file") is None or c.get("line") is None:
        problems.append("缺少定位(file/line),无法核对")
    sug = (c.get("suggestion") or "").strip()
    if not sug:
        problems.append("缺少可操作建议")
    elif not any(h in sug for h in ACTION_HINTS):
        problems.append("建议不可操作(无动作词)")
    return problems

def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    bad = 0
    for i, c in enumerate(data.get("comments", []), 1):
        probs = lint_comment(c)
        mark = "✗" if probs else "✓"
        print(f"{mark} 意见 {i} [{c.get('severity','?')}] {c.get('title','')}")
        for p in probs:
            print(f"    - {p}")
        bad += bool(probs)
    print(f"\n不合格 {bad} 条")
    return 1 if bad else 0

sys.exit(main())
