# 《AI 编程实战：写出能上生产的代码》参考来源全文（附录 G.3 各章参考来源）

纸书附录 G 只排印 G.1 分级来源索引与 G.2 多章共用来源（R1–R41）；各章参考来源全文在此。
“见附录 G 共用来源 R编号”的链接见纸书 G.2。四级可信度标签沿用全书。

以下按章节顺序列出各章正文引用的来源，标注沿用全书的四级可信度标签；在两章及以上出现的链接写作“见附录 G 共用来源 R编号”，链接见 G.2。

## 第 1 章　软件工程没有消失：从代码生成到质量可控

1. Becker, Rush, Barnes, Rein，《Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity》，METR，arXiv:2507.09089v2（2025-07）。慢 19%、预估快 24%、事后仍估快 20%、专家高估 38–39%；16 人 / 246 任务，须连作者边界一起引。见附录 G 共用来源 R1、R2
2. 同上，基于 74 段录屏约 84 小时标注的时间分配（工作重心从创造转向审查），见附录 G 共用来源 R1。
3. Stack Overflow 2025 Developer Survey：使用率 84%、信任准确性 29%（降自 40%）、46% 不信任、3% 高度信任。[survey.stackoverflow.co/2025/ai](https://survey.stackoverflow.co/2025/ai/)
4. SWE-bench Verified 官方榜单页：为公平比较模型，统一使用 mini-SWE-agent 极简环境评测。见附录 G 共用来源 R11

## 第 2 章　度量与证据：如何不被数字骗

1. SWE-bench 官方仓库（评测 Harness：任务实例 + 容器执行 + patch 应用 + 测试判定），见附录 G 共用来源 R41。
2. SWE-bench Verified 官方榜单页“apples-to-apples … mini-SWE-agent … no special scaffold structure … simple ReAct loop”统一评测声明，见附录 G 共用来源 R11。
3. DeepSeek-V3.1-Terminus 官方模型卡：SWE Verified 66.0→68.4、Terminal-bench 31.3→36.7，huggingface.co/deepseek-ai/DeepSeek-V3.1-Terminus（见附录 G 共用来源 R13）。
4. LangChain《Improving Deep Agents with Harness engineering》：模型固定（gpt-5.2-codex）只改 Harness，Terminal-Bench 2.0 52.8→66.5；位次 Top 30→Top 5 为发表当时，[blog.langchain.com/improving-deep-agents-with-harness-engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)。
5. Becker 等，《Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity》，METR，arXiv:2507.09089v2（2025-07）：慢 19%、事前估快 24%、事后仍估快 20%、接受率<44%，见附录 G 共用来源 R1。
6. Google Cloud DORA 2024/2025：2024 +25% 采用 → 吞吐 −1.5%、稳定性 −7.2%（相关非因果）；2025 90% 采用、吞吐回正、稳定性连续第二年负相关，见附录 G 共用来源 R4。
7. GitClear《Coding on Copilot》/《AI Copilot Code Quality》（约 2.11 亿行）：重构 24.8%→9.5%、复制粘贴 8.3%→12.3%（私有指标、churn 含投影、非同行评审），[gitclear.com](https://www.gitclear.com/)。
8. Veracode《2025 GenAI Code Security Report》（100+ 模型 / 80 任务）：仅 55% 安全、45% 引入 OWASP 漏洞、语法 >95% 而安全两年无进步，见附录 G 共用来源 R8。
9. Pearce 等，《Asleep at the Keyboard? Assessing the Security of GitHub Copilot's Code Contributions》，IEEE S&P 2022（1,689 个程序约 40% 含漏洞），[ieeexplore.ieee.org/document/9833571](https://ieeexplore.ieee.org/document/9833571)。
10. Stack Overflow 2025 Developer Survey：用 84% / 信 29% / 46% 不信任，[survey.stackoverflow.co/2025](https://survey.stackoverflow.co/2025/)。
11. Stripe《Minions: Stripe's one-shot, end-to-end coding Agents》及 Lenny's Newsletter 对 Steve Kaliski 专访：每周 1000→1300 PR、人类只做 review，见附录 G 共用来源 R6。
12. AWS《How frontier teams are reinventing AI-native development》（2026-06-10）：Bedrock 6 人 76 天、commit 2/周→40/周约 20×，[aws.amazon.com/blogs/machine-learning/how-frontier-teams-are-reinventing-ai-native-development](https://aws.amazon.com/blogs/machine-learning/how-frontier-teams-are-reinventing-ai-native-development/)。注：“每月 100+ PR”为，官方查无此说，不入正文。
13. Aider 官方 HISTORY / FAQ 页：“通常约 70–80%、基于 git 提交历史”及逐版本占比（v0.76.1=0%、v0.79.2=93%），aider.chat/HISTORY.html（见附录 G 共用来源 R12）。

## 第 3 章　第一代 Prompt Engineering：任务表达与指令设计

1. OpenAI，Prompt engineering（Identity/Instructions/Examples/Context 四段结构、few-shot 范例、精确指令建议、推理模型 vs GPT 模型对照），[https://platform.openai.com/docs/guides/prompt-engineering](https://platform.openai.com/docs/guides/prompt-engineering)
2. Anthropic，Prompt engineering overview（clarity、examples、XML 结构化、role prompting 等支柱与教程入口），[https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
3. Anthropic，prompt-eng-interactive-tutorial（含大量正反例的提示工程交互教程仓库），[https://github.com/anthropics/prompt-eng-interactive-tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

## 第 4 章　第二代 Context Engineering：组织模型需要的信息

1. AGENTS.md 官方站点（格式、“60k+ projects”、“88 个 AGENTS.md”、“最近文件胜出 + 用户指令覆盖一切”、Linux Foundation / Agentic AI Foundation 托管），见附录 G 共用来源 R9
2. AGENTS.md 官方仓库，[https://github.com/agentsmd/agents.md](https://github.com/agentsmd/agents.md)
3. 采用 AGENTS.md 的代表项目 openai/codex，见附录 G 共用来源 R17
4. Claude Code 记忆与 CLAUDE.md/AGENTS.md 文档（分层加载、<200 行建议、@path 导入、.claude/rules 的 paths frontmatter、“not enforced configuration / no guarantee of strict compliance”、强制用 PreToolUse hook 与 managed settings），[https://docs.claude.com/en/docs/claude-code/memory](https://docs.claude.com/en/docs/claude-code/memory)
5. Kiro Steering 文档（四种 inclusion 模式、front matter YAML 格式、product/tech/structure 三件套、#[[file:...]] 活引用、custom Agent 需显式 resources、AGENTS.md 支持），见附录 G 共用来源 R15
6. Anthropic prompt caching 定价（5min 1.25× / 1h 2× / 读取 0.1×、前缀 100% 一致），见附录 G 共用来源 R10
7. 采用 AGENTS.md 的 Aider，见附录 G 共用来源 R20

## 第 5 章　第三代 Harness Engineering：构建可控的执行环境

1. SWE-agent/mini-swe-agent 仓库（About：The 100 line AI Agent … scores >74% on SWE-bench verified），见附录 G 共用来源 R24
2. SWE-agent/SWE-agent 仓库（News：July 24——Mini-SWE-Agent achieves 65% on SWE-bench verified in 100 lines of python；“has superseded SWE-agent”），见附录 G 共用来源 R23
3. Yang et al., “SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering”, NeurIPS 2024（摘要定义 ACI，SWE-bench pass@1 12.5% / HumanEvalFix 87.7%），[https://arxiv.org/abs/2405.15793](https://arxiv.org/abs/2405.15793)
4. OpenHands（AI-Driven Development 平台，厚 Harness 代表），[https://github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
5. Aider（AI pair programming in your terminal，git 原生编辑循环），见附录 G 共用来源 R20

## 第 6 章　第四代 Loop Engineering：验证、反馈与持续改进

1. SWE-bench（Verified）官方：每个任务自带可自动运行的测试作为验证器，见附录 G 共用来源 R11
2. OpenAI GPT-5 / Codex prompting guide：停止准则、工具调用预算、逃生舱（escape hatch）等“给循环装刹车”的实操（<context_gathering> / <persistence> 块），[https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)

## 第 7 章　Anthropic：约束、安全与反馈机制

1. “调教独立评判者比让生产者自我挑剔容易”、planner+generator+evaluator、rubric 四维度、“评判产物而非路径”、成本案例、“每个部件编码会过期的假设”、“任务超出模型独自可靠范围时才值”：Anthropic《Harness design for long-running application development》，[anthropic.com/engineering/harness-design-long-running-apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)
2. 对抗式 review 用新鲜上下文、“只报影响正确性/需求的问题”反模式：Anthropic《Effective Harnesses for long-running Agents》，[anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
3. PreToolUse hook 的 stdin JSON、exit code 2 与 permissionDecision=deny、settings.json 位置、matcher、“hooks 确定性 vs CLAUDE.md 建议性”、${CLAUDE_PROJECT_DIR}、file_path 恒为绝对路径：Claude Code《Hooks reference》，[docs.claude.com/en/docs/claude-code/hooks](https://docs.claude.com/en/docs/claude-code/hooks)
4. Deny > Ask > Allow 求值顺序、allow 列表跨文件合并、deny 压 allow、permission 模式：Claude Code《Configure permissions》，[docs.claude.com/en/docs/claude-code/permissions](https://docs.claude.com/en/docs/claude-code/permissions)
5. 设置文件优先级（Managed > 命令行 > 项目本地 > 团队共享 > 用户）、列表合并规则：Claude Code《Settings files and precedence》，[docs.claude.com/en/docs/claude-code/settings](https://docs.claude.com/en/docs/claude-code/settings)
6. “每个 prompt 创建检查点”、只追踪文件编辑工具、不追踪 Bash/子 agent/外部进程、“不是版本控制替代品”：Claude Code《Checkpointing》，[docs.claude.com/en/docs/claude-code/checkpointing](https://docs.claude.com/en/docs/claude-code/checkpointing)
7. Dreaming 定义、机制（读记忆库+1–100 会话、输出独立新库、输入不被改）、研究预览、supported models：Claude Platform《Dreams》，[platform.claude.com/docs/en/managed-agents/dreams](https://platform.claude.com/docs/en/managed-agents/dreams)
8. outcomes 功能 docx +8.4% / pptx +10.1% task success（对比标准提示循环，内部基准）：Anthropic 官方博客《New in Claude Managed Agents: dreaming, outcomes, multiagent》，[claude.com/blog/new-in-claude-managed-agents](https://claude.com/blog/new-in-claude-managed-agents)（常被误归属，须写全语境）
9. PreToolUse hook 参考实现与起步配置：见附录 G 共用来源 R25，Bash 校验 hook 示例 [examples/hooks/bash_command_validator_example.py](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py)，settings 示例 [examples/settings](https://github.com/anthropics/claude-code/tree/main/examples/settings)

## 第 8 章　OpenAI：并行协作与执行环境

1. OpenAI, Harness engineering: leveraging Codex in an agent-first world（2026-02），“every line of code … has been written by Codex. We estimate … about 1/10th the time … Humans steer. Agents execute.”，[openai.com/index/harness-engineering](https://openai.com/index/harness-engineering/)。
2. OpenAI Developers, Agent approvals & security（沙箱 × 审批正交、三档预设与 CLI flag、untrusted 预设已下线、两阶段容器、secrets 提前销毁、network_proxy/allowlist/DNS rebinding、web search 缓存索引、auto-review 策略与 fail closed），见附录 G 共用来源 R17 仓库 docs/config.md 与该安全文档。
3. OpenAI Developers, Worktrees：“Worktrees let Codex run multiple independent chats in the same project without interfering with each other.” + Git 一分支一工作树约束，[developers.openai.com/codex/app/worktrees](https://developers.openai.com/codex/app/worktrees/)。
4. OpenAI Developers, Multi-agent / concepts：subagents 并行再汇总；“use parallel agents for read-heavy tasks … Be more careful with parallel write-heavy workflows, because agents editing code at once can create conflicts.”，[developers.openai.com/codex/concepts/multi-agents](https://developers.openai.com/codex/concepts/multi-agents/)。
5. OpenAI, Introducing upgrades to Codex：Codex “is trained to run commands to verify its outputs”、“provides citations, terminal logs, and test results with each task”、三档审批、云端自开浏览器附截图到 PR，[openai.com/index/introducing-upgrades-to-codex](https://openai.com/index/introducing-upgrades-to-codex/)。
6. OpenAI 对齐团队，Auto-review：人工批准频率降约 200×、对需审查动作批准约 99%、独立 reviewer、fail closed、拒绝关键风险；默认 reviewer policy 开源于 见附录 G 共用来源 R17（研究稿记录的旧深链 codex-rs/core/src/guardian/policy.md 已 404，文件路径随版本变动，故指向仓库根）。
7. AGENTS.md 规范站：Codex 自动枚举并注入 AGENTS.md、“the closest one wins”、模型受训遵守、厂商中立开放标准，agents.md（见附录 G 共用来源 R9）。AGENTS.md 的逐条写法见第 14 章，本章不展开。

## 第 9 章　Kiro：规格驱动的工程实践与适用边界

1. Kiro Docs——Specs，见附录 G 共用来源 R14（页面更新 2026-10-02）
2. Kiro Docs——Steering（含 front-matter 四种 inclusion 模式），见附录 G 共用来源 R15
3. Kiro Docs——Hooks（.kiro/hooks/*.json、version v1、字段表），[https://kiro.dev/docs/hooks/](https://kiro.dev/docs/hooks/)（页面更新 2026-09-30）
4. Kiro Docs——Hook types（PascalCase 触发类型清单），[https://kiro.dev/docs/hooks/types/](https://kiro.dev/docs/hooks/types/)
5. Kiro Docs——MCP Configuration（.kiro/settings/mcp.json 字段表），[https://kiro.dev/docs/mcp/configuration/](https://kiro.dev/docs/mcp/configuration/)（页面更新 2026-10-07）
6. AWS 官方 MCP 服务器仓库，[https://github.com/awslabs/mcp](https://github.com/awslabs/mcp)（Apache-2.0，近万 star）
7. MCP 参考实现服务器仓库，[https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)（近 10 万 star）
8. Alex Cloudstar《Spec-Driven Development in 2026: Waterfall 2.0?》2026-03（A/B 实测：实现 12 分钟 / 写规范 30 分钟 / 总耗时持平；“有两样东西要保持同步”；Agent 不总遵守规范），[https://www.alexcloudstar.com/blog/spec-driven-development-2026/](https://www.alexcloudstar.com/blog/spec-driven-development-2026/)（无明显利益冲突）
9. Markus Eisele《When AI Writes the Code, Specifications Need an Exit Strategy》O'Reilly Radar 2026-08-17（规范漂移、“第二套系统”、代码是更强信号源、退出策略；30 模型转 TLA+ 27%/9% 示意数据），[https://www.oreilly.com/radar/...](https://www.oreilly.com/radar/when-ai-writes-the-code-specifications-need-an-exit-strategy/)（无明显利益冲突）
10. Chris Zhang（Isoform）《The Limits of Spec-Driven Development》HackerNoon 2025-12-02（维护税翻倍、完整性幻觉）⚠️ 竞品平台员工，利益冲突，打折引用，[https://hackernoon.com/the-limits-of-spec-driven-development](https://hackernoon.com/the-limits-of-spec-driven-development)
11. Simon Martinelli《Why Spec-Driven Development Tools Fail in the Enterprise》2026-03-29（主流工具默认从零开始、“单行修复不应触发流水线”）⚠️ 推销自家方法论 AIUP，利益冲突，打折引用，[https://martinelli.ch/...](https://martinelli.ch/why-spec-driven-development-tools-fail-in-the-enterprise/)

## 第 10 章　开源生态：模型、Harness 与工具的分工

1. DeepSeek-V3.1 官方模型卡（smarter tool calling / post-training 优化 Agent 任务、hybrid thinking），[huggingface.co/deepseek-ai/DeepSeek-V3.1](https://huggingface.co/deepseek-ai/DeepSeek-V3.1)。
2. DeepSeek-V3.1-Terminus 官方模型卡（搜索 Agent 模板 + tool-set、agentic 基准表 SWE 66→68.4、Terminal-bench 31.3→36.7 等），huggingface.co/deepseek-ai/DeepSeek-V3.1-Terminus（见附录 G 共用来源 R13）。
3. DeepSeek API 文档（OpenAI/Anthropic 兼容端点、背书 Claude Code / Copilot / OpenCode 作后端“无需写代码”、Claude Code 接入环境变量、“DeepSeek Harness” developer preview 条目），[api-docs.deepseek.com/guides/reasoning_model](https://api-docs.deepseek.com/guides/reasoning_model)。
4. awesome-deepseek-integration（官方汇总第三方集成），[github.com/deepseek-ai/awesome-deepseek-integration](https://github.com/deepseek-ai/awesome-deepseek-integration)。
5. SWE-agent 与 ACI 设计（本章只补取舍，原理见第 5 章），见附录 G 共用来源 R23；mini-SWE-agent：见附录 G 共用来源 R24。
6. OpenHands 平台化厚 Harness，见附录 G 共用来源 R16。
7. Aider（git 原生编辑循环、安装与典型命令、Aider-Polyglot 基准、逐版本“AI 写了自己多少代码”统计），见附录 G 共用来源 R20、[aider.chat/docs/install.html](https://aider.chat/docs/install.html)、aider.chat/HISTORY.html（见附录 G 共用来源 R12）。
8. SWE-bench 评测底座与统一 mini-SWE-agent 评测声明，见附录 G 共用来源 R41。

## 第 11 章　四大流派的共性与选型：殊途同归，按处境下注

1. AGENTS.md 开放格式与多工具支持说明，见附录 G 共用来源 R9。
2. AGENTS.md 规范仓库（openai/agents.md），[https://github.com/openai/agents.md](https://github.com/openai/agents.md)。
3. DeepSeek-V3 开源模型仓库（权重开源、可自托管的底座代表），见附录 G 共用来源 R33。
4. OpenHands（重型可组装 Harness，开源生态代表之一），见附录 G 共用来源 R16。
5. SWE-agent / mini-swe-agent（薄↔厚 Harness 谱系），见附录 G 共用来源 R23 与 见附录 G 共用来源 R24。
6. Aider（开源命令行编码代理，混用生态示例），见附录 G 共用来源 R20。

## 第 12 章　代码评审：判断标准与人的责任

1. Google Engineering Practices，The Standard of Code Review（“设计几乎从不是纯风格问题”“reviewers should favor approving a CL once it … improves the overall code health”），[google.github.io/eng-practices/review/reviewer/standard.html](https://google.github.io/eng-practices/review/reviewer/standard.html)（© Google，CC BY 3.0 许可，[creativecommons.org/licenses/by/3.0](https://creativecommons.org/licenses/by/3.0/)；本书仅摘引短句并附中文转述）
2. Google Engineering Practices，What to look for in a code review（Design > Functionality > Complexity 排序、over-engineering 原文、“we expect developers to test CLs well-enough”），[google.github.io/eng-practices/review/reviewer/looking-for.html](https://google.github.io/eng-practices/review/reviewer/looking-for.html)（© Google，CC BY 3.0 许可，[creativecommons.org/licenses/by/3.0](https://creativecommons.org/licenses/by/3.0/)；本书仅摘引短句并附中文转述）
3. GitHub Docs，Copilot code review：默认只留 Comment、不计入必需审批（新增可配置的 Approve 预览功能，默认关闭），[docs.github.com/en/copilot/.../using-copilot-code-review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review)
4. OpenAI Codex code review：“another high-signal review pass”“rules … don't replace tests, branch protections, or required approvals”“only P0 and P1”，[developers.openai.com/codex/integrations/github](https://developers.openai.com/codex/integrations/github)
5. Anthropic Claude Code：多 Agent 并行 + 独立验证步骤过滤误报，定位为补充人类评审，[docs.claude.com/en/docs/claude-code/github-actions](https://docs.claude.com/en/docs/claude-code/github-actions)

## 第 13 章　代码变更管理：粒度、提交与可追溯性

1. Conventional Commits 1.0.0 规范（type/scope/description 结构、feat/fix 语义、BREAKING CHANGE、允许更多 type），[conventionalcommits.org/en/v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)。
2. commitlint 文档与仓库（CLI、config-conventional、husky commit-msg 集成），[commitlint.js.org](https://commitlint.js.org/)、[github.com/conventional-changelog/commitlint](https://github.com/conventional-changelog/commitlint)。
3. Architectural Decision Records 组织主页（ADR 定义、decision log、Michael Nygard 2011 推广、MADR 等模板），[adr.github.io](https://adr.github.io/)。
4. joelparkerhenderson/architecture-decision-record（ADR 模板与示例合集），[github.com/joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record)。
5. 变更行数上限（非机械 800 / 复杂逻辑 500 / 超了拆成可评审阶段）、模块规模（<500 LoC、>800 开新模块），openai/codex 仓库 codex-rs/AGENTS.md，见附录 G 共用来源 R17。
6. Stripe Minions 每周合入 1,000→1,300+ PR、人类主要做 review，Stripe 开发者博客 / Lenny's Newsletter 采访。引用纪律：仅作描述性事实，不得呈现为团队应追求的目标数字。，见附录 G 共用来源 R6

## 第 14 章　工程规范的可执行化

1. OpenHands AGENTS.md（仓库身份、主要验证命令、依赖方向、HUMAN: 段人机边界等原文），见附录 G 共用来源 R16。
2. import-linter（layers 契约、lint-imports 用法；本章用 v2.15 本机跑通），见附录 G 共用来源 R19。
3. ruff（F401 未用导入、RET505 多余 else；本章用 v0.16.10 本机跑通），见附录 G 共用来源 R21。
4. pre-commit（第二层门禁标准工具），[https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)。
5. dependency-cruiser（JS/TS 结构测试工具），[https://github.com/sverweij/dependency-cruiser](https://github.com/sverweij/dependency-cruiser)。
6. ArchUnit（Java 结构测试工具），[https://github.com/TNG/ArchUnit](https://github.com/TNG/ArchUnit)。
7. uv（本章 Demo 的运行器 uv run --with），见附录 G 共用来源 R18。

## 第 15 章　测试：验证行为与测试本身的有效性

1. Hypothesis（Python 属性测试库），见附录 G 共用来源 R29（近万 star）。
2. mutmut（Python 变异测试系统），见附录 G 共用来源 R22（数千 star；文档 [mutmut.readthedocs.io](https://mutmut.readthedocs.io)）。
3. Schemathesis（基于 schema 的 API Fuzz/契约测试），见附录 G 共用来源 R39（数千 star）。
4. Pact（消费者驱动契约测试，Python 版），[https://github.com/pact-foundation/pact-python](https://github.com/pact-foundation/pact-python)（数百 star；生态文档 [docs.pact.io](https://docs.pact.io)）。
5. opencode 的 AGENTS.md 测试规矩（尽量不用 mock、禁止从根跑测试 guard do-not-run-tests-from-root、用 typecheck 不用 tsc），见附录 G 共用来源 R28（条目属易变内容）。
6. Veracode《2025 GenAI Code Security Report》：约 45% AI 生成代码引入 OWASP 类漏洞、安全通过率两年约 55%（样本与口径见本书第 2 章），见附录 G 共用来源 R8。
7. AI 在模块边界最易出错（隐性上下文缺失），METR，arXiv:2507.09089（讨论见本书第 2 章），见附录 G 共用来源 R1。

## 第 16 章　Code Review Agent

1. OpenAI, “Review GitHub pull requests with Codex”（another high-signal review pass、@codex review、Automatic review、only P0/P1、规则不替代测试/分支保护/必需审批、机械检查留 CI、## Code Review Rules、@codex fix the P1 issue），[developers.openai.com/codex/code-review](https://developers.openai.com/codex/code-review)
2. GitHub Docs, “Using GitHub Copilot code review”（默认只留 Comment、不计必需审批；High/Med/Low 严重度；Lite/Balanced effort 原话；Approve 为公开预览需显式开启；读 AGENTS.md/skills/MCP），[docs.github.com/en/copilot/how-tos/agents/copilot-code-review/using-copilot-code-review](https://docs.github.com/en/copilot/how-tos/agents/copilot-code-review/using-copilot-code-review)
3. Anthropic, “Claude Code GitHub Actions”（@claude 触发、可分析/改代码/提交、交互与自动两模式、code-review 示例工作流、最小权限 permissions、fork PR 不下发 secrets），见附录 G 共用来源 R31
4. Anthropic, claude-code code review 机制（multiple Agents in parallel + verification step filters false positives 原话），Claude Code 文档 code-review 页，[code.claude.com/docs/en/code-review](https://code.claude.com/docs/en/code-review)
5. Astral, ruff（--output-format=json schema、规则码、自动修复），见附录 G 共用来源 R21 及 [docs.astral.sh/ruff/configuration](https://docs.astral.sh/ruff/configuration/)
6. CodeRabbit, F1 51.2%（引 Martian）及“用推理层复核静态分析降误报”，[coderabbit.ai/blog/boosting-static-analysis-accuracy-with-ai](https://www.coderabbit.ai/blog/boosting-static-analysis-accuracy-with-ai)（跨厂商不可直接比）
7. Greptile, F1 60.8% / precision 76.2% / recall 50.6%（引 Martian），[greptile.com/content-library/greptile-martian-code-review-benchmark](https://www.greptile.com/content-library/greptile-martian-code-review-benchmark)（跨厂商不可直接比）
8. Qodo, F1 60.1% / recall 56.7%，[qodo.ai/blog/introducing-qodo-2-0-agentic-code-review](https://www.qodo.ai/blog/introducing-qodo-2-0-agentic-code-review/)（跨厂商不可直接比）
9. Copilot code review 单次成本 Lite ~$0.05–$1 / Balanced ~$0.25–$5（含 AI credits、不含 Actions 分钟），GitHub Copilot code review 文档（会随定价变动）

## 第 17 章　Security Agent：检出、修复与它自己的风险

1. GitHub Blog《Found means fixed: Introducing code scanning autofix》（覆盖 90%+ 告警类型、约 2/3 可零/少编辑修复），[github.blog](https://github.blog/news-insights/product-news/found-means-fixed-introducing-code-scanning-autofix-powered-by-github-copilot-and-codeql/)
2. GitHub Blog《Fixing security vulnerabilities with AI》（Autofix 机制：CodeQL 检出 → 发 LLM 生成修复），[github.blog](https://github.blog/2024-02-14-fixing-security-vulnerabilities-with-ai/)
3. GitHub docs（Autofix “best-effort，不保证 100% 成功”），[docs.github.com](https://docs.github.com/code-security/code-scanning/managing-code-scanning-alerts/about-autofix-for-codeql-code-scanning)
4. GitHub changelog（Actions 场景：15.8 万+ 仓库、80 万+ 漏洞、约 15% 被实际修复）——检出≠修复的关键数字，[github.blog/changelog/2025-04-22-…](https://github.blog/changelog/2025-04-22-github-actions-workflow-security-analysis-with-codeql-is-now-generally-available/)
5. Semgrep 2025 系列博客（约 60% 新 SAST 发现先 triage / 与研究员一致率 96% / 用户认可 95% / 25 万+ 发现 45+ 企业；triage Memories），[semgrep.dev/blog](https://semgrep.dev/blog/)
6. GitHub changelog（Dependabot 告警可指派给 AI Agent 开草稿 PR）；Snyk Code + Snyk Agent Fix，[snyk.io](https://snyk.io/)
7. Anthropic（Claude Code 自动安全评审 /security-review、覆盖类型、补丁交人类审阅），[anthropic.com/news](https://www.anthropic.com/news)；OpenAI Codex Security Review
8. Anthropic news（Alberta 省政府用 Claude Code 审查系统/找漏洞/修复），[anthropic.com/news/alberta-government-claude-cybersecurity](https://www.anthropic.com/news/alberta-government-claude-cybersecurity)
9. Anthropic news（安全评测中三起模型未授权访问真实系统事故），[anthropic.com/news/investigating-incidents-cybersecurity-evals](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals)
10. gitleaks 见附录 G 共用来源 R35（HTTP 200，已声明 feature complete）、bandit 见附录 G 共用来源 R30、pip-audit 见附录 G 共用来源 R27、CodeQL Action 见附录 G 共用来源 R34、Semgrep [github.com/semgrep/semgrep](https://github.com/semgrep/semgrep)

## 第 18 章　DevOps Agent：调查、受控执行与审计闭环

1. AWS DevOps Agent 定位“investigates production incidents and proposes or applies fixes on your behalf”、Agent journal 不可变抗注入、UpdateApprovalAction 审批、默认角色 848 action 近乎全只读——“Audit trails for autonomous agents with AWS DevOps Agent”，AWS DevOps Blog（2026-09），[aws.amazon.com/blogs/devops/audit-trails-for-autonomous-agents-with-aws-devops-agent](https://aws.amazon.com/blogs/devops/audit-trails-for-autonomous-agents-with-aws-devops-agent/)
2. Property Finder 端到端 14 分钟（>88% 降幅）、“The PR is always opened as Draft … The agent never auto-merges”、每会话只读 guardrail、“the agent accelerates, the engineer decides”——“How Property Finder automated incident management with AWS DevOps Agent”，AWS DevOps Blog（2026-09），[aws.amazon.com/blogs/devops/how-property-finder-automated-incident-management-with-aws-devops-agent](https://aws.amazon.com/blogs/devops/how-property-finder-automated-incident-management-with-aws-devops-agent/)
3. Amazon CloudWatch operational investigations：“scan your system's telemetry and quickly surface suggestions”、告警进 ALARM 自动启动调查——AWS CloudWatch 文档 · Investigations，[docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Investigations.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Investigations.html)
4. k8sgpt：扫描/诊断/分诊、SRE 经验固化进 analyzer、CNCF Sandbox / Apache-2.0、内置 MCP server（k8sgpt serve --mcp）——仓库 README，[github.com/k8sgpt-ai/k8sgpt](https://github.com/k8sgpt-ai/k8sgpt)
5. HolmesGPT：“The CNCF SRE Agent”、read-only access、respects RBAC、订阅 Alertmanager——仓库 README，[github.com/HolmesGPT/holmesgpt](https://github.com/HolmesGPT/holmesgpt)
6. Kubernetes MCP Server：Go 原生实现、read_only=true 与 denied_resources、推荐专用 ServiceAccount + 只读——仓库 README（Apache-2.0），[github.com/containers/kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server)
7. AWS DevOps Agent 审计样例仓库（供进一步实践）——[github.com/aws-samples/sample-audit-patterns-for-aws-devops-agent](https://github.com/aws-samples/sample-audit-patterns-for-aws-devops-agent)

## 第 19 章　AI 时代的 CI/CD 与多 Agent 治理

1. Meta AI，《Agents Rule of Two: A Practical Approach to AI Agent Security》（2025-10-31，Rule of Two 原始出处，含 [A][B][C] 原文、受 Chromium Rule of 2 与 lethal trifecta 启发），[ai.meta.com/blog/practical-ai-agent-security](https://ai.meta.com/blog/practical-ai-agent-security/)
2. Microsoft Threat Intelligence，《Securing CI/CD in an agentic world: Claude Code GitHub Action case》——完整攻击链、Read 工具不在沙箱、读取进程环境变量、变形绕过扫描、引用并应用 Rule of Two、MITRE ATLAS 技法映射（2026-06-05），见附录 G 共用来源 R7
3. GitHub Actions《Events that trigger workflows》——pull_request_target 在 base 默认分支上下文运行、workflow_run “able to access secrets and write tokens” 及其安全警告，[docs.github.com](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
4. GitHub Actions OpenID Connect（id-token: write 换云端临时凭证），[docs.github.com/en/actions/concepts/security/openid-connect](https://docs.github.com/en/actions/concepts/security/openid-connect)
5. anthropics/claude-code-action 官方 docs/security.md——“Do not check out an untrusted ref into the workspace root”、base/head 子目录、配置文件从 base 恢复、allowed_non_write_users 标 RISKY、show_full_output 默认关、“user must click the link… ensuring human oversight”，[github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)
6. anthropics/claude-code-action 官方 examples/claude.yml（OIDC/联邦认证、actions: read 读 CI、concurrency/timeout-minutes/模型分级），[github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml)
7. openai/codex 仓库 .github/workflows/issue-labeler.yml（只读沙箱 + safety-strategy: drop-sudo + output-schema + if: github.repository == 防 fork），[github.com/openai/codex](https://github.com/openai/codex/blob/main/.github/workflows/issue-labeler.yml)
8. OpenAI《Codex auto-fix on CI failure》/ non-interactive-mode——“generate_fix 只读 / open_pr 有写无 OPENAI_API_KEY”、“不要把 API key 设 job 级 env”、--json/--output-schema，见附录 G 共用来源 R17
9. All-Hands-AI/OpenHands live E2E 凭证隔离（fork PR 在 checkout 前跳过、key 只注入受信步骤、关 Playwright trace），见附录 G 共用来源 R16
10. github/codeql-action（确定性检出引擎，分层门禁的确定性一侧），见附录 G 共用来源 R34
11. OpenAI/Anthropic/Google DeepMind 合著论文——12 种已发布防御可被自适应攻击者 >90% 绕过（2025-10），见附录 G 共用来源 R3
12. OWASP：prompt injection 列为 LLM Top 10 #1 风险，见附录 G 共用来源 R5
13. “Comment and Control” 跨厂商漏洞（影响 Claude Code / Gemini CLI / GitHub Copilot），SecurityWeek / CybersecurityNews（2026）
14. PromptPwnd（GitHub Actions / GitLab CI 与 AI Agent 结合的新供应链漏洞类），Aikido Security
15. CI agentic workflow 注入分类 P2A / P2S，GitHub Actions 中该类漏洞的首个系统研究，arXiv
16. MITRE ATLAS 技法（T0051 Prompt Injection / T0053 Tool Invocation / T0098 Credential Harvesting / T0057 Data Leakage），作检测分类骨架，[d3fend.mitre.org/offensive-technique/attack/AML.T0051](https://d3fend.mitre.org/offensive-technique/attack/AML.T0051/)

## 第 20 章　项目启动：交付可运行的工程基线

1. AWS AI-DLC（AI-Driven Development Life Cycle）开源工作流，[https://github.com/awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows)（5 phases/33 stages、human approval gates、source-bound evidence 等定义引自其 README）。
2. AWS AI-DLC 官方博客，[https://aws.amazon.com/blogs/devops/](https://aws.amazon.com/blogs/devops/)（AI-DLC 方法博客）。
3. uv，见附录 G 共用来源 R18；ruff，见附录 G 共用来源 R21。
4. mypy，[https://github.com/python/mypy](https://github.com/python/mypy)；import-linter，见附录 G 共用来源 R19。
5. pre-commit-hooks，[https://github.com/pre-commit/pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)；gitleaks，见附录 G 共用来源 R35。
6. OpenHands（结构测试守越层调用的真实先例），见附录 G 共用来源 R16（见第 1、2 章）。

## 第 21 章　产品与需求：交付邀请功能的规格

1. Alistair Mavin，EARS（来历、通用结构、规则集、六句式与官方例句、“gently constrain”措辞、使用者含 Intel），[alistairmavin.com/ears](https://alistairmavin.com/ears/)。
2. Alistair Mavin 等，Ten Years of EARS（EARS 发展与应用），[ResearchGate 335535918](https://www.researchgate.net/publication/335535918_Ten_Years_of_EARS)。
3. Kiro Docs，Specs（requirements/design/tasks 三件套、三阶段工作流、任务分波并行），见附录 G 共用来源 R14（页面更新 2026-10-02）。
4. GitHub，Spec Kit（开源 SDD 工具包，安装命令 uv tool install specify-cli / specify init，MIT 许可），[github.com/github/spec-kit](https://github.com/github/spec-kit)。
5. Astral，uv（Spec Kit 依赖的 Python 包管理器），见附录 G 共用来源 R18。
6. Can LLMs Write Correct TLA+ Specifications? Evaluating Natural-Language-to-TLA+ Generation：LLM 把自然语言需求转为 TLA+ 规范，语法正确率最高 26.6%、语义正确率仅 8.6%，[arxiv.org/abs/2606.05792](https://arxiv.org/abs/2606.05792)。用于说明“别指望 AI 生成的规范天然可靠”。

## 第 22 章　架构与设计：交付决策、契约与安全约束

1. Microsoft Learn，Microsoft Threat Modeling Tool threats（STRIDE 六类定义原文），[learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)。
2. Microsoft，Security Development Lifecycle（SDL）——“在问题易于、低成本修复的早期识别并缓解”的生命周期化安全思想，[learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)。
3. import-linter（分层契约门禁），见附录 G 共用来源 R19。
4. openapi-spec-validator（OpenAPI 契约校验），[github.com/python-openapi/openapi-spec-validator](https://github.com/python-openapi/openapi-spec-validator)。
5. schemathesis（基于契约的 API 测试，可选替代），见附录 G 共用来源 R39。
6. PostgreSQL（集成测试数据库），[github.com/postgres/postgres](https://github.com/postgres/postgres)。
7. 多租户三种隔离模型（共享表+tenant_id / schema-per-tenant / db-per-tenant），分类依据 Microsoft Azure 多租户架构指南与 AWS SaaS 隔离白皮书。

## 第 23 章　后端开发：交付接口、测试与迁移

1. FastAPI 官方文档与仓库，[github.com/fastapi/fastapi](https://github.com/fastapi/fastapi)
2. SQLAlchemy 官方仓库，[github.com/sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy)
3. Alembic 官方仓库（迁移 upgrade/downgrade），见附录 G 共用来源 R40
4. Pydantic 官方仓库，[github.com/pydantic/pydantic](https://github.com/pydantic/pydantic)
5. pytest 官方仓库，见附录 G 共用来源 R38
6. uv（Astral）官方仓库，见附录 G 共用来源 R18
7. PostgreSQL 文档：Partial Indexes（部分索引），[postgresql.org/docs/current/indexes-partial.html](https://www.postgresql.org/docs/current/indexes-partial.html)
8. GitHub Docs：Copilot coding Agent（Agent 产出走同样的 PR/CI/审批流程），[docs.github.com/en/copilot …/coding-agent](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/about-assigning-tasks-to-copilot)
9. Martin Fowler：ParallelChange（expand/contract 模式），[martinfowler.com/bliki/ParallelChange.html](https://martinfowler.com/bliki/ParallelChange.html)

## 第 24 章　前端开发：交付可验证的邀请流程

1. Vite，[github.com/vitejs/vite](https://github.com/vitejs/vite)（200）
2. React，[github.com/facebook/react](https://github.com/facebook/react)（200）
3. TypeScript，[github.com/microsoft/TypeScript](https://github.com/microsoft/TypeScript)（200）
4. Vitest，[github.com/vitest-dev/vitest](https://github.com/vitest-dev/vitest)（200）
5. Testing Library（React），[github.com/testing-library/react-testing-library](https://github.com/testing-library/react-testing-library)（200）
6. Playwright，见附录 G 共用来源 R26（200）
7. openapi-typescript，见附录 G 共用来源 R37（200）
8. axe-core（@axe-core/playwright），[github.com/dequelabs/axe-core-npm](https://github.com/dequelabs/axe-core-npm)、[github.com/dequelabs/axe-core](https://github.com/dequelabs/axe-core)（均 200）

## 第 25 章　测试与评审：交付质量证据

1. pytest 官方仓库，见附录 G 共用来源 R38。
2. mutmut 官方仓库，见附录 G 共用来源 R22。
3. Hypothesis 官方仓库，见附录 G 共用来源 R29。
4. Playwright 官方仓库，见附录 G 共用来源 R26。
5. bandit 官方仓库，见附录 G 共用来源 R30。
6. pip-audit 官方仓库，见附录 G 共用来源 R27。

## 第 26 章　部署与发布：完成上线与回滚演练

1. aws-actions/configure-aws-credentials（OIDC 用法、role-to-assume/aws-region、id-token:write、信任策略 sub/StringLike、禁 ForAllValues、不可变 sub claim、当前版本 v6.3.0），[https://github.com/aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
2. AWS CDK 仓库，见附录 G 共用来源 R32
3. Docker CLI 仓库，[https://github.com/docker/cli](https://github.com/docker/cli)
4. AWS CLI 仓库，[https://github.com/aws/aws-cli](https://github.com/aws/aws-cli)
5. astral-sh/uv（容器内依赖管理与锁定），见附录 G 共用来源 R18
6. Amazon ECS 部署熔断自动回滚、deploymentConfiguration 配 CloudWatch alarms 与 bake time，AWS Containers 博客《Automate rollbacks for Amazon ECS rolling deployments with CloudWatch alarms》与《Announcing Amazon ECS deployment circuit breaker》，[https://aws.amazon.com/blogs/containers/announcing-amazon-ecs-deployment-circuit-breaker/](https://aws.amazon.com/blogs/containers/announcing-amazon-ecs-deployment-circuit-breaker/)
7. AWS CodeDeploy ECS 蓝绿 + canary/linear 流量切换、ALB 加权目标组、CloudWatch 告警自动切回，AWS Containers 博客与 CDK aws_codedeploy 文档，[https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_codedeploy-readme.html](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_codedeploy-readme.html)

## 第 27 章　运行与维护：交付运行记录与改进结果

1. Google SRE Book, Chapter 4 “Service Level Objectives”（SLI/SLO/SLA 与错误预算定义），[https://sre.google/sre-book/service-level-objectives/](https://sre.google/sre-book/service-level-objectives/)
2. pip-audit（PyPA 官方依赖漏洞扫描），见附录 G 共用来源 R27
3. Prometheus Python Client，[https://github.com/prometheus/client_python](https://github.com/prometheus/client_python)
4. OpenTelemetry Python（CNCF），[https://github.com/open-telemetry/opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python)
5. Michael Feathers, 《Working Effectively with Legacy Code》——特征测试（characterization test）概念来源

## 第 28 章　Sprint：节奏、承诺与交付能力

1. The 2020 Scrum Guide（Sprint 定义、“Quality does not decrease”、Definition of Done 与 Increment 的关系、Sprint Planning 中产能与 DoD 的作用、Daily Scrum），Ken Schwaber & Jeff Sutherland，[https://scrumguides.org/scrum-guide.html](https://scrumguides.org/scrum-guide.html)。
2. METR, “Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity”（资深开发者在熟悉大仓库中用 AI 反而变慢、事前事后判断反向、工作重心转向审查），arXiv:2507.09089，见附录 G 共用来源 R1（完整数字见第 2 章）。
3. DORA 年度报告（AI 采用度上升与交付稳定性下降的相关关系，连续两年），完整数字与口径见第 2 章。
4. GitClear 代码质量研究（重构信号下降、复制粘贴反超重构），完整数字见第 2 章。
5. Conventional Commits 规范（提交信息格式 type(scope): summary，用于 DoD 门禁），[https://github.com/conventional-commits/conventionalcommits.org](https://github.com/conventional-commits/conventionalcommits.org)。
6. import-linter（分层架构契约检查，用作结构测试门禁），见附录 G 共用来源 R19。
7. mutmut（Python 变异测试工具，用以证明断言有效性），见附录 G 共用来源 R22。

## 第 29 章　回顾与改进：让经验进入下一轮工作

1. ruff 文档 flake8-tidy-imports（banned-api / TID251）规则，astral-sh/ruff，见附录 G 共用来源 R21（本机 ruff 0.16.10 实测 TID251 生效）。
2. 前端直连后端的结构测试思路，All-Hands-AI/OpenHands，见附录 G 共用来源 R16。
3. “不预先抽取只用一次的 helper”、PR 行数上限等 AGENTS.md 约定，openai/codex、sst/opencode，见附录 G 共用来源 R17、R28。
4. 变异测试工具 mutmut（用于揭穿弱断言假测试，第 15、25 章），boxed/mutmut，见附录 G 共用来源 R22。

## 第 30 章　团队协作与评价：把个人提速转化为交付收益

1. DORA, “DORA's software delivery performance metrics”（四/五指标定义、改进起点、常见陷阱），[https://dora.dev/guides/dora-metrics-four-keys/](https://dora.dev/guides/dora-metrics-four-keys/)。
2. N. Forsgren, M.-A. Storey, C. Maddila, T. Zimmermann, B. Houck, J. Butler, “The SPACE of Developer Productivity,” ACM Queue, 2021（SPACE 五维与“至少跨三维”原则），[https://dl.acm.org/doi/10.1145/3453928](https://dl.acm.org/doi/10.1145/3453928)。
3. Microsoft, “Navigating the SPACE between productivity and developer happiness”（SPACE 五维：Satisfaction, Performance, Activity, Communication, Efficiency），[azure.microsoft.com/en-us/blog/navigating-the-space-between-productivity-and-developer-happiness](https://azure.microsoft.com/en-us/blog/navigating-the-space-between-productivity-and-developer-happiness/)。

## 第 31 章　软件工程师：从直接实现到组织交付

1. 开发者主观提速与实际耗时相反、用过仍反向校准：METR 随机对照研究（2025），本书第 2、10 章转述其结论。见附录 G 共用来源 R2
2. “使用率越高、信任度越低”趋势：Stack Overflow 开发者调查，本书只取方向性结论，见第 2 章。

## 第 32 章　架构师：设计业务系统与研发环境

1. Architectural fitness function（架构适应度函数定义），ThoughtWorks Technology Radar，[thoughtworks.com/radar/techniques/architectural-fitness-function](https://www.thoughtworks.com/radar/techniques/architectural-fitness-function)。原文定义其溯源自《Building Evolutionary Architectures》一书。
2. 《Building Evolutionary Architectures》（Neal Ford, Rebecca Parsons, Patrick Kua），ThoughtWorks，[thoughtworks.com/books/building-evolutionary-architectures](https://www.thoughtworks.com/books/building-evolutionary-architectures)——适应度函数概念的原始出处。
3. Cyclomatic complexity（圈复杂度），McCabe, T.J.，“A Complexity Measure”，IEEE TSE, 1976；概念综述见 [en.wikipedia.org/wiki/Cyclomatic_complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)。
4. Python ast 模块文档，[docs.python.org/3/library/ast.html](https://docs.python.org/3/library/ast.html)——Demo 32-1 使用的标准库。
5. 禁改沙箱环境变量 CODEX_SANDBOX_*，openai/codex 仓库 AGENTS.md，见附录 G 共用来源 R17。
6. HUMAN: 段 AI 不得编辑、前端不得直连 endpoint 的 CI guard，All-Hands-AI/OpenHands 仓库 AGENTS.md，见附录 G 共用来源 R16。
7. 多租户三种隔离模型（共享 schema / 独立 schema / 独立库）——业界公认的经典分类；“对 AI 的风险”维度为本书论点。

## 第 33 章　AI 时代的工程能力：训练、校准与成长

1. Anthropic, “How AI assistance impacts the formation of coding skills”（RCT，n=52，AI 组测验 50% vs 手写 67%，Cohen's d=0.738, p=0.01，调试题差距最大；四类能力；高/低分交互模式；agentic 工具影响更大），2026-01-29，[https://www.anthropic.com/research/AI-assistance-coding-skills](https://www.anthropic.com/research/AI-assistance-coding-skills)
2. Shen & Tamkin, “How AI Impacts Skill Formation”, arXiv:2601.20245（上文博客对应论文），[https://arxiv.org/abs/2601.20245](https://arxiv.org/abs/2601.20245)
3. METR, “Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity”（RCT：熟悉大仓库上 AI 使完成时间 +19%，CI +2%~+39%，开发者自评快 20%），2025-07-10，见附录 G 共用来源 R2
4. Microsoft Research, “The Impact of Generative AI on Critical Thinking”（CHI 2025，319 名知识工作者问卷：对 AI 的信心越高、自报告的批判性思维越少；属自评/非因果，证据较弱），[microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-…](https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/)

## 第 34 章　合理使用 Token：平衡质量、时间与成本

1. Anthropic，“Prompt caching”（倍数 1.25×/2×/0.1×、最小长度四档、失效层级、回看 20 block、反模式案例、total_input 口径、自动缓存同坑），见附录 G 共用来源 R10。
2. OpenAI tiktoken 开源分词器仓库（第 34 章 Token 计数所用工具），[github.com/openai/tiktoken](https://github.com/openai/tiktoken)。

## 第 35 章　不让软件工程失控

1. An alignment assessment of recent cybersecurity incidents，Anthropic（对约 141,000 条评测轨迹扫描后确认 4 起未授权访问事件，其中 3 起于 2026-07-30 披露），[https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents)
2. GitHub REST API：Update branch protection（PUT /repos/{owner}/{repo}/branches/{branch}/protection，含 required_pull_request_reviews、enforce_admins 字段），[https://docs.github.com/en/rest/branches/branch-protection](https://docs.github.com/en/rest/branches/branch-protection)
3. GitHub CLI gh api 使用说明，[https://cli.github.com/manual/gh_api](https://cli.github.com/manual/gh_api)

## 附录 A　范式与流派速查：关键事件时间线、能力对照与选型索引

1. OpenAI Codex 仓库与非交互文档，见附录 G 共用来源 R17、[developers.openai.com/codex](https://developers.openai.com/codex/)。
2. Anthropic Claude Code 仓库，见附录 G 共用来源 R25。
3. “Harness Engineering” 命名归属 Mitchell Hashimoto，[mitchellh.com/writing](https://mitchellh.com/writing)（若发现更早一手出处应前移）。
4. AGENTS.md 厂商中立、Linux Foundation 托管，agents.md（见附录 G 共用来源 R9）。
5. DeepSeek “做底座不做框架”，见附录 G 共用来源 R33。

## 附录 B　项目资料包：AGENTS.md 模板与 TeamPulse 规格、仓库结构及提示词

1. astral-sh/uv，见附录 G 共用来源 R18。
2. seddonym/import-linter（分层契约），见附录 G 共用来源 R19。
3. sqlalchemy/alembic（迁移），见附录 G 共用来源 R40。
4. aws/aws-cdk（IaC），见附录 G 共用来源 R32。
5. microsoft/playwright（E2E），见附录 G 共用来源 R26。
6. openapi-ts/openapi-typescript（契约生成类型），见附录 G 共用来源 R37。

## 附录 C　质量自动化参考：门禁清单、验证器与 Hooks 配置样例

1. CI 分层提速（PR 快检查 / 合并后全量矩阵）、safety-strategy/sandbox/output-schema，openai/codex（见附录 G 共用来源 R17） 与 openai/codex-action（见附录 G 共用来源 R36）。
2. 结构测试 no-direct-agent-server-calls.test.ts、依赖方向约束，OpenHands（见附录 G 共用来源 R16） 与 opencode（见附录 G 共用来源 R28） 的 AGENTS.md。
3. pre-commit、detect-secrets、gitleaks、ruff、mutmut、Stryker、Playwright、axe-core 官方仓库（见表 C-3）。
4. Claude Code hooks（.claude/settings.json），anthropics/claude-code（见附录 G 共用来源 R25）。
5. Kiro steering/specs/hooks，[kiro.dev](https://kiro.dev/)（具体字段以官方文档为准）。

## 附录 D　安全交付检查清单：CI/CD 加固、发布审批与回滚

1. CI 提示注入完整攻击链、Agents Rule of Two、硬化 system prompt 范本，Microsoft Threat Intelligence 博客《Securing CI/CD in an agentic world》，2026-06-05，见附录 G 共用来源 R7。
2. 读写分离双 job（generate_fix 只读 / open_pr 有写无 key），OpenAI Codex non-interactive-mode / autofix-ci 文档。
3. OIDC/联邦认证、fork PR 禁令“Do not check out an untrusted ref…”、成本四板斧、show_full_output 默认关，claude-code-action（见附录 G 共用来源 R31） 与其 security.md。
4. 结构化输出 --output-schema、“不要把 API key 设 job 级 env”、权限档/safety-strategy，openai/codex-action（见附录 G 共用来源 R36） README 与 openai/codex（见附录 G 共用来源 R17）。
5. live E2E 用真 LLM key 的凭证隔离清单（fork PR 在 checkout 前跳过、key 只注入受信步骤、关 Playwright trace），OpenHands（见附录 G 共用来源 R16） 的 AGENTS.md。
6. 12 种已发布防御可被自适应攻击者 >90% 绕过，OpenAI/Anthropic/Google DeepMind 合著论文，2025-10，见附录 G 共用来源 R3。
7. OWASP LLM Top 10 把 prompt injection 列为 #1，见附录 G 共用来源 R5。

## 附录 E　团队改进工具：Token 优化清单、回顾会模板与度量看板

1. Anthropic，“Prompt caching”（缓存三类 Token 的 total_input = cache_read + cache_creation + input 口径、写入 1.25×/2× 读取 0.1× 倍数、最小可缓存长度四档、失效层级 tools→system→messages、断点反模式与自动缓存同坑），见附录 G 共用来源 R10。
2. OpenHands 仓库结构测试 no-direct-agent-server-calls.test.ts（前端直连后端的机械约束示例），见附录 G 共用来源 R16。
3. opencode / codex 仓库 AGENTS.md（“不预先抽取只用一次的辅助函数”的 Steering 规则、“非机械变更不超过 800 行”的行数门禁），见附录 G 共用来源 R17。
4. DORA（DevOps Research and Assessment）四大交付指标：交付周期、部署频率、变更失败率、恢复时间（本附录交付周期与变更失败率的口径依据），见附录 G 共用来源 R4。
5. METR, “Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity”（资深开发者对加速的反向误判，支撑“对着数字而非感觉开会”），见附录 G 共用来源 R2。
