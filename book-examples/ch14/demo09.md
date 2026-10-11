# AGENTS.md

> 本文件是给自动化编码 agent 的 steering 指令，不是给人的贡献指南。
> agent：下面每一条都当硬约束字面遵守；标"先问人"的动作执行前必须停下确认。

## 构建与验证（↔ 守卫：CI 跑这些命令）
- 主要验证命令：`[npm run lint]`、`[npm test]`、`[npm run build]`。改完代码必须跑完这几个。
- 一律用项目封装入口 `[just test]`，不要直接调底层工具 `[cargo test]`（以带上默认配置）。
- 只跑受改动影响的那个包的测试；运行完整测试套件前先问人。

## 变更规模（↔ 守卫：PR 行数检查）
- 非机械性变更总行数不超过 [800] 行；复杂逻辑控制在 [500] 行以下，更大就拆成可评审的阶段。

## 依赖方向（↔ 守卫：import-linter / 结构测试，见 14.5）
- 运行时依赖方向：[api] → [service] → [repo]；下层绝不能 import 上层。
- 该约束由 `[.importlinter]` 契约守卫，越界 CI 失败。

## 代码风格（↔ 守卫：ruff，见 14.3）
- 禁止未使用的导入（F401）；优先早返回、避免多余 else（RET505）；禁止用 `any` 绕过类型检查。
- 这些由 `[ruff.toml]`（select = ["F","RET",...]）守卫，提交前跑 `ruff check`。

## 提交格式（↔ 守卫：pre-commit commit 格式钩子）
- 提交与 PR 标题用 `type(scope): summary`，type 限 [feat/fix/docs/chore/refactor/test]。

## 禁区：agent 不得触碰（↔ 守卫：权限层 deny + CI guard）
- 不得添加或修改任何与 [安全/沙箱环境变量名] 相关的代码。
- PR 描述里的 `HUMAN:` 段为人类专属，MUST NOT 添加/编辑/移动/删除；
  CI 因它缺失而失败时，停下来请人用自己的话补写，不要自行填充。
