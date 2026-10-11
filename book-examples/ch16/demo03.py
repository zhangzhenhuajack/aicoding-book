import json
import sys

# ruff 规则码 -> AI 的 category，用来判断"是不是同一类机械问题"
RUFF_CATEGORY = {
    "F401": "style", "F541": "style", "F841": "style",
    "E711": "logic", "E712": "logic", "B008": "logic",
}
SEV_RANK = {"P0": 0, "P1": 1, "P2": 2}   # P0 最高


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def norm_ruff(items):
    """把 ruff 原生条目规整成与 AI 条目同构的字典。"""
    out = []
    for it in items:
        out.append({
            "path": it["filename"],
            "line": it["location"]["row"],
            "severity": "P2",   # 风格/机械问题统一按低优先级进评论
            "category": RUFF_CATEGORY.get(it["code"], "static"),
            "message": f'[{it["code"]}] {it["message"]}',
            "source": "ruff",
            "fixable": bool(it.get("fix")),
        })
    return out


def key(item):
    """去重键：同一文件、同一行、同一类别，视为同一个问题。"""
    return (item["path"], item["line"], item["category"])


def merge(ai_items, ruff_items):
    merged = {}
    for it in ruff_items:                    # 先放 ruff（确定性来源优先）
        merged[key(it)] = dict(it, also_from=[])
    for it in ai_items:                      # 再合并 AI
        k = key(it)
        if k in merged:                      # 重叠：以 ruff 为准，只标记 AI 也提到
            merged[k]["also_from"].append("ai")
        else:
            merged[k] = dict(it, fixable=False, also_from=[])
    rows = list(merged.values())
    rows.sort(key=lambda r: (SEV_RANK.get(r["severity"], 9), r["path"], r["line"]))
    return rows


def render(rows):
    print(f"合并后共 {len(rows)} 条（去重前 AI+ruff 相加会更多）\n")
    for r in rows:
        tag = "+".join(["ai" if r["source"] == "ai" else r["source"], *r["also_from"]])
        fix = " [可自动修复]" if r.get("fixable") else ""
        dup = "  <- AI 与 ruff 重叠，已折叠为一条" if r["also_from"] else ""
        print(f'  {r["severity"]:3s} {r["path"]}:{r["line"]:<4d} ({r["category"]}/{tag}){fix}')
        print(f'       {r["message"]}{dup}')


def main():
    ai_items = load(sys.argv[1])
    ruff_items = norm_ruff(load(sys.argv[2]))
    rows = merge(ai_items, ruff_items)
    render(rows)
    # 有 P0/P1 则非零退出：在 CI 里当"需人工关注"的信号，但这不是门禁
    hi = sum(1 for r in rows if SEV_RANK.get(r["severity"], 9) <= 1)
    sys.exit(1 if hi else 0)


if __name__ == "__main__":
    main()
