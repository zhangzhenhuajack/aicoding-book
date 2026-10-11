#!/usr/bin/env python3
"""rubric 评分：把"好不好"拆成带权重的维度，让独立评判者逐项打分。本书示例。"""
from dataclasses import dataclass

# rubric：维度 + 权重（权重就是价值观的显式化；originality 刻意给高以打 AI slop）
RUBRIC = {
    "functionality": 0.30,  # 功能是否跑通（最硬，可机械判定）
    "design":        0.25,  # 设计质量
    "originality":   0.25,  # 原创性（高权重，专打"白卡片+紫渐变"）
    "craft":         0.20,  # 做工细节
}
PASS_LINE = 0.70  # 达标线

@dataclass
class Candidate:
    name: str
    scores: dict  # 每个维度 0.0–1.0，由独立评判者给出

def grade(c: Candidate) -> dict:
    """评判产物（而非路径）：只看最终各维度得分。"""
    weighted = sum(RUBRIC[d] * c.scores.get(d, 0.0) for d in RUBRIC)
    weak = sorted((d for d in RUBRIC if c.scores.get(d, 0.0) < 0.6),
                  key=lambda d: c.scores.get(d, 0.0))
    return {"name": c.name, "total": round(weighted, 3),
            "passed": weighted >= PASS_LINE, "weakest": weak}

def main() -> None:
    candidates = [
        Candidate("A_白卡片紫渐变", {"functionality": 0.9, "design": 0.5,
                                     "originality": 0.2, "craft": 0.6}),
        Candidate("B_有点想法的版本", {"functionality": 0.85, "design": 0.8,
                                       "originality": 0.75, "craft": 0.7}),
    ]
    print(f"达标线 = {PASS_LINE}；rubric 权重 = {RUBRIC}\n")
    for c in candidates:
        r = grade(c)
        verdict = "✅ 通过" if r["passed"] else "❌ 打回重做"
        print(f"[{r['name']}] 加权总分={r['total']}  {verdict}")
        if not r["passed"]:
            dims = "、".join(f"{d}({c.scores[d]})" for d in r["weakest"])
            print(f"    → 不达标维度：{dims}；别再用那套紫色渐变，提高原创性再交。")
        print()

if __name__ == "__main__":
    main()
