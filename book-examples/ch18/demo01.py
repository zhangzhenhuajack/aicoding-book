#!/usr/bin/env python3
"""Demo 18-1：只读诊断 agent 的"工具层"（本书示例）。

四个工具 + 一个权限闸门：
  1) correlate_alerts  —— 告警去重 + 按 service/window 关联成一个 incident
  2) read_evidence     —— 只读拉取样例日志 / 指标 / 变更记录
  3) hypothesize       —— 产出根因假设 + 证据清单（不碰生产）
  4) gated_action      —— 任何"写操作"必须过人工审批闸门，默认拒绝

全部用本机样例数据跑通，不连接任何真实集群。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta


# ---------- 样例数据（本机，不出网） ----------
NOW = datetime(2026, 10, 8, 3, 2, 0)

RAW_ALERTS = [
    {"id": "a1", "service": "checkout", "name": "HighLatencyP99", "ts": NOW},
    {"id": "a2", "service": "checkout", "name": "HighLatencyP99", "ts": NOW + timedelta(seconds=40)},
    {"id": "a3", "service": "checkout", "name": "DBConnPoolExhausted", "ts": NOW + timedelta(seconds=55)},
    {"id": "a4", "service": "checkout", "name": "HighLatencyP99", "ts": NOW + timedelta(seconds=70)},
    {"id": "a5", "service": "search", "name": "HighLatencyP99", "ts": NOW + timedelta(minutes=9)},
]

SAMPLE_LOGS = {
    "checkout": [
        "03:01:12 WARN  HikariPool-1 - Connection is not available, request timed out after 30000ms",
        "03:01:40 ERROR could not get a connection from pool (active=50, idle=0, max=50)",
        "03:02:05 ERROR could not get a connection from pool (active=50, idle=0, max=50)",
    ],
    "search": ["03:11:00 WARN  slow query > 800ms on index=products"],
}

SAMPLE_METRICS = {
    "checkout": {"db_conn_active": 50, "db_conn_max": 50, "p99_ms": 4200, "p99_baseline_ms": 320},
    "search": {"p99_ms": 910, "p99_baseline_ms": 450},
}

SAMPLE_CHANGES = [
    {"ts": NOW - timedelta(minutes=12), "service": "checkout",
     "change": "deploy v8.3.1: set spring.datasource.hikari.maximum-pool-size=50 (was 200)"},
    {"ts": NOW - timedelta(days=2), "service": "search", "change": "reindex products catalog"},
]


# ---------- 工具 1：告警去重 + 关联 ----------
def correlate_alerts(alerts, window_s=120):
    """同 service、同窗口内的告警归并成一个 incident；重复 name 只记一次 + 计数。"""
    alerts = sorted(alerts, key=lambda a: a["ts"])
    incidents = []
    for a in alerts:
        placed = False
        for inc in incidents:
            if inc["service"] == a["service"] and (a["ts"] - inc["last_ts"]).total_seconds() <= window_s:
                inc["signals"].setdefault(a["name"], 0)
                inc["signals"][a["name"]] += 1
                inc["raw_count"] += 1
                inc["last_ts"] = a["ts"]
                placed = True
                break
        if not placed:
            incidents.append({
                "service": a["service"], "first_ts": a["ts"], "last_ts": a["ts"],
                "raw_count": 1, "signals": {a["name"]: 1},
            })
    return incidents


# ---------- 工具 2：只读证据拉取 ----------
def read_evidence(service):
    return {
        "logs": SAMPLE_LOGS.get(service, []),
        "metrics": SAMPLE_METRICS.get(service, {}),
        "recent_changes": [c for c in SAMPLE_CHANGES if c["service"] == service],
    }


# ---------- 工具 3：根因假设 + 证据清单 ----------
@dataclass
class Hypothesis:
    service: str
    root_cause: str
    confidence: str
    evidence: list = field(default_factory=list)
    suggested_fix: str = ""


def hypothesize(incident, evidence):
    svc = incident["service"]
    m = evidence["metrics"]
    ev = []
    root = "未定位（证据不足）"
    conf = "低"
    fix = ""
    pool_full = m.get("db_conn_active") and m.get("db_conn_active") == m.get("db_conn_max")
    if "DBConnPoolExhausted" in incident["signals"] and pool_full:
        ev.append(f"指标：db_conn_active={m['db_conn_active']} 已打满 max={m['db_conn_max']}")
        ev.append(f"指标：p99={m['p99_ms']}ms，基线 {m['p99_baseline_ms']}ms（放大 {m['p99_ms'] // m['p99_baseline_ms']}x）")
        for line in evidence["logs"]:
            if "pool" in line.lower():
                ev.append(f"日志：{line}")
        for c in evidence["recent_changes"]:
            if "pool-size" in c["change"]:
                ev.append(f"变更：{c['ts']:%H:%M} {c['change']}")
                root = "新部署把连接池上限从 200 调到 50，高峰期连接耗尽导致 p99 飙升"
                conf = "高"
                fix = "回滚 v8.3.1 或将 maximum-pool-size 调回 200"
    return Hypothesis(service=svc, root_cause=root, confidence=conf, evidence=ev, suggested_fix=fix)


# ---------- 工具 4：权限闸门（写操作默认拒绝） ----------
WRITE_ACTIONS = {"rollback", "scale", "restart", "patch_config", "delete_pod"}


class ApprovalRequired(Exception):
    pass


def gated_action(action, target, approved_by=None, dry_run=True):
    """任何写操作必须：①被人工审批 ②非 dry_run 才真正执行。
    本 demo 永不真正触达生产——只演示闸门逻辑。"""
    if action in WRITE_ACTIONS:
        if not approved_by:
            raise ApprovalRequired(
                f"动作 '{action}' 作用于 '{target}' 属于写操作，被闸门拦下：需人工审批后才能执行。"
            )
        return {"status": "approved", "action": action, "target": target,
                "approved_by": approved_by, "executed": not dry_run,
                "note": "demo 中 dry_run=True，不会真正执行"}
    return {"status": "readonly_ok", "action": action, "target": target}


def main():
    print("=" * 60)
    print("只读诊断 agent 工具层 · 本机样例跑通")
    print("=" * 60)

    print(f"\n[1] correlate_alerts：{len(RAW_ALERTS)} 条原始告警 → 关联去重")
    incidents = correlate_alerts(RAW_ALERTS)
    for i, inc in enumerate(incidents, 1):
        print(f"    incident#{i}  service={inc['service']}  "
              f"原始告警={inc['raw_count']}  去重信号={inc['signals']}")

    target = incidents[0]
    print(f"\n[2] read_evidence：拉取 service={target['service']} 的只读证据")
    evidence = read_evidence(target["service"])
    print(f"    日志 {len(evidence['logs'])} 行 / 指标 {len(evidence['metrics'])} 项 "
          f"/ 近期变更 {len(evidence['recent_changes'])} 条")

    print("\n[3] hypothesize：根因假设 + 证据清单")
    h = hypothesize(target, evidence)
    print(f"    根因假设：{h.root_cause}")
    print(f"    置信度：{h.confidence}")
    print("    证据清单：")
    for e in h.evidence:
        print(f"      - {e}")
    print(f"    建议修复：{h.suggested_fix}")

    print("\n[4] gated_action：权限闸门")
    r1 = gated_action("read_evidence", target["service"])
    print(f"    只读动作 → {r1['status']}")
    try:
        gated_action("rollback", "checkout/v8.3.1")
    except ApprovalRequired as e:
        print(f"    写操作(未审批) → 被拦下：{e}")
    r3 = gated_action("rollback", "checkout/v8.3.1", approved_by="oncall@team", dry_run=True)
    print(f"    写操作(已审批) → {r3['status']}，executed={r3['executed']}（{r3['note']}）")

    print("\n输出 JSON（可供上层 agent 消费）：")
    print(json.dumps({
        "incidents": [{"service": i["service"], "signals": i["signals"],
                       "raw_count": i["raw_count"]} for i in incidents],
        "hypothesis": {"service": h.service, "root_cause": h.root_cause,
                       "confidence": h.confidence, "evidence": h.evidence,
                       "suggested_fix": h.suggested_fix},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
