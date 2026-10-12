#!/usr/bin/env python3
"""项目约定「一源多方言」转换器（本书示例）。

读入一份与厂商无关的项目约定（conventions.yaml 的极简子集，
用标准库手写解析，无需第三方依赖），同时生成：
  - AGENTS.md        （OpenAI / 多工具通用，厂商中立）
  - CLAUDE.md        （Anthropic Claude Code）
  - .kiro/steering/*.md（Kiro，按加载模式拆分）

一处修改、三处同步，避免手工维护三份导致漂移。
"""
from __future__ import annotations

import sys
from pathlib import Path


def parse_simple_yaml(text: str) -> dict:
    """解析本 demo 用到的极简 YAML 子集：
    顶层 key: 标量 / 列表（- 开头）/ 两层嵌套 map。
    不依赖 PyYAML，便于读者照抄即可跑。
    """
    data: dict = {}
    cur_key = None
    cur_list: list | None = None
    cur_map: dict | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0:
            cur_list = cur_map = None
            if line.endswith(":"):
                cur_key = line[:-1].strip()
                data[cur_key] = None  # 待定：下文决定是 list 还是 map
            else:
                k, _, v = line.partition(":")
                data[k.strip()] = v.strip()
                cur_key = None
        else:  # 缩进行
            if line.startswith("- "):
                if not isinstance(data.get(cur_key), list):
                    data[cur_key] = cur_list = []
                cur_list.append(line[2:].strip())
            else:
                if not isinstance(data.get(cur_key), dict):
                    data[cur_key] = cur_map = {}
                k, _, v = line.partition(":")
                cur_map[k.strip()] = v.strip()
    return data


def md_list(items: list[str]) -> str:
    return "\n".join(f"- {it}" for it in items)


def gen_agents_md(c: dict) -> str:
    return f"""# AGENTS.md

> 本文件由 conventions.yaml 自动生成，请勿手工编辑；改约定请改源文件后重跑转换器。

## 项目：{c.get('project', '未命名')}

{c.get('summary', '')}

## 构建与验证命令
{md_list(c.get('commands', []))}

## 约束（违反即构建失败）
{md_list(c.get('constraints', []))}

## 变更规模上限
- 单个 PR 变更不超过 {c.get('limits', {}).get('max_pr_lines', 'N/A')} 行
- 单文件不超过 {c.get('limits', {}).get('max_file_lines', 'N/A')} 行

## 权限边界
{md_list(c.get('permissions', []))}
"""


def gen_claude_md(c: dict) -> str:
    # Claude Code 读 CLAUDE.md；内容与 AGENTS.md 同源，仅标题与口吻微调。
    return f"""# CLAUDE.md

<!-- 自动生成，勿手工编辑；源文件 conventions.yaml -->

你正在 **{c.get('project', '未命名')}** 仓库中工作。{c.get('summary', '')}

## 必须遵守的命令
{md_list(c.get('commands', []))}

## 硬约束（Deny 优先）
{md_list(c.get('constraints', []))}

## 变更规模
- PR ≤ {c.get('limits', {}).get('max_pr_lines', 'N/A')} 行；单文件 ≤ {c.get('limits', {}).get('max_file_lines', 'N/A')} 行

## 权限
{md_list(c.get('permissions', []))}
"""


def gen_kiro_steering(c: dict) -> dict[str, str]:
    """Kiro 的 steering 按加载模式拆成多文件。"""
    always = f"""---
inclusion: always
---
# 项目约定（自动生成，源：conventions.yaml）

项目：{c.get('project', '未命名')}。{c.get('summary', '')}

命令：
{md_list(c.get('commands', []))}
"""
    constraints = f"""---
inclusion: always
---
# 硬约束与规模上限（自动生成）

{md_list(c.get('constraints', []))}

- PR ≤ {c.get('limits', {}).get('max_pr_lines', 'N/A')} 行；单文件 ≤ {c.get('limits', {}).get('max_file_lines', 'N/A')} 行
"""
    perms = f"""---
inclusion: manual
---
# 权限边界（按需加载，自动生成）

{md_list(c.get('permissions', []))}
"""
    return {
        "product.md": always,
        "constraints.md": constraints,
        "permissions.md": perms,
    }


def main(src_path: str, out_dir: str) -> None:
    out = Path(out_dir)
    c = parse_simple_yaml(Path(src_path).read_text(encoding="utf-8"))

    (out / "AGENTS.md").write_text(gen_agents_md(c), encoding="utf-8")
    (out / "CLAUDE.md").write_text(gen_claude_md(c), encoding="utf-8")
    steer = out / ".kiro" / "steering"
    steer.mkdir(parents=True, exist_ok=True)
    for name, body in gen_kiro_steering(c).items():
        (steer / name).write_text(body, encoding="utf-8")

    print("已从一份约定生成三种方言：")
    print(f"  {out / 'AGENTS.md'}")
    print(f"  {out / 'CLAUDE.md'}")
    for name in gen_kiro_steering(c):
        print(f"  {steer / name}")
    print("\nAGENTS.md 预览（前 14 行）：")
    print("\n".join((out / "AGENTS.md").read_text(encoding="utf-8").splitlines()[:14]))


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "conventions.yaml"
    dst = sys.argv[2] if len(sys.argv) > 2 else "out"
    Path(dst).mkdir(parents=True, exist_ok=True)
    main(src, dst)
