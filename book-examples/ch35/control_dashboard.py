#!/usr/bin/env python3
"""失控信号仪表（本书示例）

从一份仓库指标 JSON 计算四个失控信号的占比/次数，与阈值比较，
任一越线就输出"建议暂停"。指标口径：
  - unreviewed_merge_ratio   未评审就合并的 PR 占比
  - test_assertion_edits     测试断言被改写的次数（近 N 次提交内）
  - gate_bypass_count        门禁被绕过（--no-verify / 跳过 CI）的次数
  - unexplained_diff_ratio   无人能解释的 diff 占比（评审记录里标 "不确定/没看懂"）

用法：
  python3 control_dashboard.py metrics.json
不给文件时用内置样例数据。
"""
import json
import sys

# 阈值（本书示例取值，团队应按自己的基线校准）
THRESHOLDS = {
    "unreviewed_merge_ratio": 0.10,   # 未评审合并 > 10%
    "test_assertion_edits": 3,        # 断言被改写 > 3 次
    "gate_bypass_count": 0,           # 门禁绕过 > 0 次（零容忍）
    "unexplained_diff_ratio": 0.15,   # 无法解释的 diff > 15%
}

# 每个信号对应书中的"三道防线"里的哪一道
DEFENSE = {
    "unreviewed_merge_ratio": "人类闸门",
    "test_assertion_edits": "验证器",
    "gate_bypass_count": "验证器",
    "unexplained_diff_ratio": "人类闸门",
}

LABEL = {
    "unreviewed_merge_ratio": "未评审就合并的比例",
    "test_assertion_edits": "测试断言被改写次数",
    "gate_bypass_count": "门禁被绕过次数",
    "unexplained_diff_ratio": "无法解释的 diff 比例",
}

SAMPLE = {
    "repo": "teampulse-demo",
    "window": "最近 50 次合并",
    "unreviewed_merge_ratio": 0.18,
    "test_assertion_edits": 5,
    "gate_bypass_count": 2,
    "unexplained_diff_ratio": 0.08,
}


def is_ratio(key):
    return key.endswith("_ratio")


def fmt(key, value):
    return f"{value:.0%}" if is_ratio(key) else str(value)


def evaluate(metrics):
    rows, breached = [], []
    for key, limit in THRESHOLDS.items():
        value = metrics.get(key, 0)
        over = value > limit
        rows.append((key, value, limit, over))
        if over:
            breached.append(key)
    return rows, breached


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            metrics = json.load(f)
    else:
        metrics = SAMPLE

    rows, breached = evaluate(metrics)
    print(f"失控信号仪表 · 仓库 {metrics.get('repo', '?')} · {metrics.get('window', '')}")
    print("=" * 56)
    print(f"{'信号':<22}{'实测':>7}{'阈值':>7}  状态   对应防线")
    print("-" * 56)
    for key, value, limit, over in rows:
        status = "✗越线" if over else "✓正常"
        print(f"{LABEL[key]:<20}{fmt(key, value):>7}{fmt(key, limit):>7}  {status}  {DEFENSE[key]}")
    print("=" * 56)

    if breached:
        print(f"\n⛔ 建议暂停：{len(breached)} 个信号越线，防线正在失效。")
        for key in breached:
            print(f"   - {LABEL[key]} 触发「{DEFENSE[key]}」失效，需人工介入核查。")
        sys.exit(1)
    else:
        print("\n✅ 全部正常：四道信号均在阈值内，可继续自动化流程。")
        sys.exit(0)


if __name__ == "__main__":
    main()
