import re
import subprocess
import sys

MAX_PR_LINES = 500  # 与 AGENTS.md 一致（示意阈值）


def gate_commit_message(msg: str):
    """提交信息须符合 Conventional Commits：type(scope): summary。"""
    ok = bool(re.match(r"^(feat|fix|docs|refactor|test|chore|perf)(\([^)]+\))?: .+", msg))
    return ok, f"首行={msg.splitlines()[0]!r}"


def gate_pr_size(added: int, deleted: int):
    """非机械变更 PR 行数上限。"""
    total = added + deleted
    return total <= MAX_PR_LINES, f"改动 {total} 行（上限 {MAX_PR_LINES}）"


def gate_human_rationale(pr_body: str):
    """PR 描述必须有人填写的 HUMAN: 段，且非空、非占位。"""
    m = re.search(r"HUMAN:\s*(.+)", pr_body)
    filled = bool(m and m.group(1).strip() and "TODO" not in m.group(1))
    return filled, "HUMAN 段已填" if filled else "HUMAN 段缺失或占位"


def gate_command(name: str, cmd: list[str]):
    """封装真实命令门禁（ruff/mypy/pytest 等）：退出码 0 即通过。"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return r.returncode == 0, f"$ {' '.join(cmd)} -> exit {r.returncode}"
    except FileNotFoundError:
        return False, f"命令不存在: {cmd[0]}"


def run_dod(sample):
    checks = [
        ("提交信息格式", *gate_commit_message(sample["commit_msg"])),
        ("PR 行数上限", *gate_pr_size(sample["added"], sample["deleted"])),
        ("HUMAN 变更理由", *gate_human_rationale(sample["pr_body"])),
        # 真实项目取消注释，接到仓库：
        # ("Lint", *gate_command("ruff", ["ruff", "check", "."])),
        # ("类型检查", *gate_command("mypy", ["mypy", "--strict", "app"])),
        # ("测试", *gate_command("pytest", ["pytest", "-q"])),
    ]
    print(f"=== DoD 门禁：{sample['label']} ===")
    all_ok = True
    for name, ok, evidence in checks:
        all_ok &= ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:12s} — {evidence}")
    print(f"  => {'可合并（全部门禁通过）' if all_ok else '阻断合并（存在未通过门禁）'}\n")
    return all_ok


if __name__ == "__main__":
    good = {
        "label": "合格 PR",
        "commit_msg": "feat(invitations): add expiry check for accept endpoint",
        "added": 180, "deleted": 40,
        "pr_body": "## 变更\n实现 REQ-INV-006\nHUMAN: 过期判定放服务层，避免 API 层散落时间逻辑。",
    }
    bad = {
        "label": "不合格 PR（AI 一把梭）",
        "commit_msg": "update stuff",
        "added": 1900, "deleted": 260,
        "pr_body": "done\nHUMAN: TODO",
    }
    results = [run_dod(good), run_dod(bad)]
    sys.exit(0 if all(results) else 1)  # 任一样本未过即非零退出，可接进 CI
