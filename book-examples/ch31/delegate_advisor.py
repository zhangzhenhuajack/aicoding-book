#!/usr/bin/env python3
"""委派判断清单：输入任务的四个属性，输出委派建议与理由。"""
from dataclasses import dataclass


@dataclass
class Task:
    name: str
    verifiability: int   # 0-3 越高越可机械验证
    risk: int            # 0-3 越高越危险
    context_full: int    # 0-3 越高上下文越完整
    coord_cost: int      # 0-3 越高协调越贵


def advise(t: Task) -> dict:
    reasons = []
    delegable = t.verifiability + t.context_full      # 0-6 可委派分
    friction = t.risk + t.coord_cost                  # 0-6 阻力分
    score = delegable - friction                      # -6..+6

    if t.verifiability <= 1:
        reasons.append("可验证性低——AI 产出无客观裁决，'看起来对'会蒙混过关，必须人来把关")
    else:
        reasons.append("可验证性高——有客观验证器可把 AI 逼到合格线")
    if t.risk >= 2:
        reasons.append("风险高——出错影响面大/不可逆，委派也必须保留人类闸门")
    if t.context_full <= 1:
        reasons.append("上下文不完整——隐性约定多，AI 容易在错方向上精确执行")
    if t.coord_cost >= 2:
        reasons.append("协调成本高——讲清楚的功夫可能超过自己做，碎活不值得委派")

    if score >= 3 and t.risk <= 1:
        verdict = "交给 AI（可放手）"
    elif score >= 1:
        verdict = "人机协作（AI 执行 + 人验收，高风险处人工复核）"
    elif t.verifiability <= 1 and t.context_full <= 1:
        verdict = "人亲自做（AI 大概率帮倒忙）"
    else:
        verdict = "人机协作（先补上下文/造验证器，再逐步放手）"

    return {"task": t.name, "verdict": verdict, "score": score,
            "delegable": delegable, "friction": friction, "reasons": reasons}


def render(r: dict) -> str:
    out = [f"【{r['task']}】 => {r['verdict']}",
           f"  委派分={r['delegable']}  阻力分={r['friction']}  净分={r['score']:+d}"]
    for why in r["reasons"]:
        out.append(f"  - {why}")
    return "\n".join(out)


if __name__ == "__main__":
    samples = [
        Task("给已有 REST 接口补一个分页参数（有契约测试）",
             verifiability=3, risk=1, context_full=3, coord_cost=1),
        Task("重构核心计费模块的金额取整逻辑",
             verifiability=2, risk=3, context_full=2, coord_cost=2),
        Task("决定整个系统该拆成几个微服务",
             verifiability=0, risk=2, context_full=1, coord_cost=3),
        Task("把登录页按钮文案从'登录'改成'立即登录'",
             verifiability=1, risk=0, context_full=3, coord_cost=0),
    ]
    for s in samples:
        print(render(advise(s)))
        print()
