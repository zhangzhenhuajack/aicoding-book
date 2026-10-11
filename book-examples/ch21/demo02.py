#!/usr/bin/env python3
"""检查 requirements.md 里每条 REQ-INV-xxx 是否符合 EARS 结构。
机械能查三件事（语义仍须人审）：句式关键词、编号+验收线索、模糊词。
用法：python3 check_ears.py requirements.md
"""
import re, sys

VAGUE = ["快速", "友好", "尽量", "合理", "易用", "及时", "适当", "良好", "高效", "方便"]
PATTERNS = [
    (re.compile(r"如果.*那么"), "Unwanted(If-Then)"),   # 模式 5
    (re.compile(r"当.*期间"), "State(While)"),           # 模式 2
    (re.compile(r"当.*时"), "Event(When)"),              # 模式 3
    (re.compile(r"在.*中|在.*场合"), "Optional(Where)"), # 模式 4
]
COMPLEX = re.compile(r"当.*期间.*当.*时")                # 模式 6：While+When
HAS_SHALL = re.compile(r"应(当)?")
HAS_STATUS = re.compile(r"\b(20[01]|40[0-9]|41[0-9]|422)\b|错误码|schema")

def classify(body):
    if COMPLEX.search(body): return "Complex"
    for rx, name in PATTERNS:
        if rx.search(body): return name
    return "Ubiquitous" if HAS_SHALL.search(body) else None   # 无关键词+有 shall=普遍式

def main():
    text = open(sys.argv[1], encoding="utf-8").read()
    blocks = re.split(r"\*\*(REQ-INV-\d+)[｜|]([^\*]+)\*\*", text)
    reqs = [(blocks[i], blocks[i+1].strip(), blocks[i+2].strip())
            for i in range(1, len(blocks), 3)]
    print(f"扫描 {sys.argv[1]}，共发现 {len(reqs)} 条需求\n")
    fails = 0
    for rid, title, body in reqs:
        problems = []
        pat = classify(body)
        if pat is None: problems.append("未命中任何 EARS 句式（缺触发/状态/shall）")
        if not HAS_SHALL.search(body): problems.append("缺少系统响应标志词『应/应当』")
        if not HAS_STATUS.search(body): problems.append("缺少可验证的验收线索（状态码/错误码）")
        vague = [w for w in VAGUE if w in body]
        if vague: problems.append(f"含模糊词：{'、'.join(vague)}")
        if problems: fails += 1
        print(f"[{'OK  ' if not problems else 'FAIL'}] {rid} {title}  -> {pat or '?'}")
        for p in problems: print(f"         · {p}")
    print(f"\n结果：{len(reqs)-fails}/{len(reqs)} 条通过结构检查，{fails} 条需修。")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
