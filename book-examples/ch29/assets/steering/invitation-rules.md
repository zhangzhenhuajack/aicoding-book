# Invitation 规则（Steering 样例 · 已腐烂）

本文件是一份演示用的 Steering 资产，部分引用已失效，用来演示 Demo 29-2 的
资产过期检查器如何扫出 Stale 资产。

## 校验脚本

跨租户隔离由 `scripts/check_tenant_isolation.sh` 守护（该脚本已在重构中删除——失效引用）。

分层方向仍由真实存在的架构测试 `test_layering.py` 守护（有效引用，作为对照）。

## 本地跑法

```bash
flake8-legacy app/
```
