#!/usr/bin/env python3
"""紧急刹车：冻结自动合并（本书示例）

当失控信号越线时，用这个脚本一键"拉闸"——冻结 AI/自动化的合并权限。
真实环境用 GitHub CLI 把分支保护打开（需要人类凭据，AI 够不着）：

  gh api -X PUT repos/:owner/:repo/branches/main/protection \
    -F enforce_admins=true \
    -F 'required_pull_request_reviews[required_approving_review_count]=2' \
    -F 'restrictions[users][]=release-captain'

本脚本默认 --dry-run，只打印将要执行的命令并写一个本地 FREEZE 文件做
本机模拟，不真正调用网络；加 --execute 才会尝试调用 gh（需已登录）。
"""
import argparse
import pathlib
import subprocess
import sys

FREEZE_FILE = pathlib.Path("MERGE_FROZEN.flag")

GH_COMMANDS = [
    # 1) 收紧 main 分支保护：强制 2 人评审 + 管理员也不能绕过
    [
        "gh", "api", "-X", "PUT",
        "repos/{owner}/{repo}/branches/main/protection",
        "-F", "enforce_admins=true",
        "-F", "required_pull_request_reviews[required_approving_review_count]=2",
    ],
    # 2) 把自动合并机器人从可写名单移除（示意）
    [
        "gh", "api", "-X", "DELETE",
        "repos/{owner}/{repo}/collaborators/automerge-bot",
    ],
]


def render(cmd, owner, repo):
    return [c.format(owner=owner, repo=repo) for c in cmd]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", default="your-org")
    ap.add_argument("--repo", default="teampulse")
    ap.add_argument("--reason", default="失控信号越线，人工拉闸")
    ap.add_argument("--execute", action="store_true", help="真正调用 gh（默认只演练）")
    args = ap.parse_args()

    print("紧急刹车 · 冻结自动合并")
    print("=" * 52)
    print(f"目标仓库 : {args.owner}/{args.repo}")
    print(f"原因     : {args.reason}")
    mode = "执行(--execute)" if args.execute else "演练(dry-run)"
    print(f"模式     : {mode}")
    print("-" * 52)

    print("将要执行的 gh 命令：")
    for cmd in GH_COMMANDS:
        print("  $ " + " ".join(render(cmd, args.owner, args.repo)))

    if args.execute:
        for cmd in GH_COMMANDS:
            real = render(cmd, args.owner, args.repo)
            try:
                subprocess.run(real, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"  [失败] {e}（请确认已 gh auth login 且有权限）")
                sys.exit(1)
        print("已通过 gh 收紧分支保护。")
    else:
        # 本机模拟：写一个冻结标记文件，CI 可据此拒绝自动合并
        FREEZE_FILE.write_text(f"frozen: {args.reason}\n", encoding="utf-8")
        print("-" * 52)
        print(f"[本机模拟] 已写入冻结标记：{FREEZE_FILE}")
        print("  CI 可在合并前检查此文件存在即拒绝自动合并。")

    print("=" * 52)
    print("✅ 刹车动作完成。解除冻结需人工删除标记 / 恢复分支保护。")


if __name__ == "__main__":
    main()
