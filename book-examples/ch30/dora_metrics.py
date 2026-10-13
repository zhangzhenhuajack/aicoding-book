#!/usr/bin/env python3
"""从样例 git/PR/部署事件计算 DORA 四个关键指标，并对比"PR 数量"指标的误导性。

所有事件数据均为【示意数据】，用于演示计算口径，不代表任何真实团队。
DORA 四指标口径依据 Google Cloud DORA 官方定义。
"""
import statistics
from datetime import datetime

FMT = "%Y-%m-%d %H:%M"


def t(s): return datetime.strptime(s, FMT)


# 每条部署事件：commit_at, deployed_at, failed, restored_at（示意数据）
# Q2 相比 Q1：PR 数量翻倍，但失败率上升、恢复变慢、前置时间变长。
DEPLOYS = {
    "Q1": [
        ("2026-01-05 09:00", "2026-01-05 15:00", False, None),
        ("2026-01-12 10:00", "2026-01-13 10:00", False, None),
        ("2026-01-20 09:30", "2026-01-20 18:30", False, None),
        ("2026-02-02 09:00", "2026-02-02 14:00", True, "2026-02-02 15:00"),
        ("2026-02-15 09:00", "2026-02-16 09:00", False, None),
        ("2026-02-25 09:00", "2026-02-25 17:00", False, None),
        ("2026-03-10 09:00", "2026-03-10 13:00", False, None),
        ("2026-03-22 09:00", "2026-03-23 09:00", False, None),
    ],
    "Q2": [
        ("2026-04-02 09:00", "2026-04-03 21:00", False, None),
        ("2026-04-06 09:00", "2026-04-08 09:00", True, "2026-04-08 15:00"),
        ("2026-04-10 09:00", "2026-04-12 09:00", False, None),
        ("2026-04-15 09:00", "2026-04-16 20:00", True, "2026-04-17 08:00"),
        ("2026-04-20 09:00", "2026-04-22 09:00", False, None),
        ("2026-05-02 09:00", "2026-05-04 09:00", False, None),
        ("2026-05-08 09:00", "2026-05-09 22:00", True, "2026-05-10 12:00"),
        ("2026-05-14 09:00", "2026-05-16 09:00", False, None),
        ("2026-05-20 09:00", "2026-05-22 15:00", True, "2026-05-23 09:00"),
        ("2026-06-01 09:00", "2026-06-03 09:00", False, None),
        ("2026-06-10 09:00", "2026-06-12 09:00", False, None),
        ("2026-06-20 09:00", "2026-06-22 18:00", True, "2026-06-23 10:00"),
    ],
}
PR_MERGED = {"Q1": 42, "Q2": 95}       # "PR 数量"产出指标（示意数据）
QUARTER_DAYS = {"Q1": 90, "Q2": 91}


def hours(a, b): return (t(b) - t(a)).total_seconds() / 3600.0


def compute(q):
    rows = DEPLOYS[q]
    n = len(rows)
    fails = [r for r in rows if r[2]]
    lead = [hours(c, d) for (c, d, _f, _r) in rows]
    recov = [hours(d, r) for (_c, d, f, r) in rows if f and r]
    return {
        "deploy_freq_per_week": round(n / (QUARTER_DAYS[q] / 7), 2),
        "lead_time_median_h": round(statistics.median(lead), 1),
        "change_failure_rate": round(len(fails) / n * 100, 1),
        "recovery_median_h": round(statistics.median(recov), 1) if recov else 0.0,
        "pr_merged": PR_MERGED[q],
    }


def row(label, a, b, unit, lower_is_better):
    arrow = "↑" if b > a else ("↓" if b < a else "→")
    good = (b <= a) if lower_is_better else (b >= a)
    return f"  {label:<22}{a:>8}{unit}  →{b:>8}{unit}  {arrow} {'✅' if good else '⚠️'}"


def main():
    q1, q2 = compute("Q1"), compute("Q2")
    print("产出指标（容易误导）：PR 数量")
    print(row("合并 PR 数", q1["pr_merged"], q2["pr_merged"], " 个", False))
    g = round((q2["pr_merged"] / q1["pr_merged"] - 1) * 100)
    print("  → 仅看 PR：产出增长 %d%%，会得出「团队提速明显」。\n" % g)
    print("DORA 四个关键指标（交付能力的真实画像）")
    print(row("部署频率", q1["deploy_freq_per_week"], q2["deploy_freq_per_week"], " 次/周", False))
    print(row("变更前置时间(中位)", q1["lead_time_median_h"], q2["lead_time_median_h"], " 小时", True))
    print(row("变更失败率", q1["change_failure_rate"], q2["change_failure_rate"], " %", True))
    print(row("失败恢复时间(中位)", q1["recovery_median_h"], q2["recovery_median_h"], " 小时", True))


if __name__ == "__main__":
    main()
