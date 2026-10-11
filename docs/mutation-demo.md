# 变异测试演示：一个假测试被揭穿、补强后杀死变异体

> 本文件是真实可复现的过程记录，所有命令与输出均来自本仓库实际运行（2026-10-08）。

## 背景

被测对象是领域层的过期判定 `app/domain/invitation.py::Invitation.is_expired`：

```python
def is_expired(self, now: datetime) -> bool:
    """过期判定：当前时间 >= expires_at（REQ-INV-006）。"""
    return now >= self.expires_at
```

需求 REQ-INV-006 规定"邀请 7 天后过期"。这里的边界语义是：**当 `now` 恰好等于
`expires_at` 时，应判为已过期**（用 `>=` 而不是 `>`）。边界行为正是变异测试最擅长照出来的地方。

## 关于 mutmut 工具

本仓库在 `pyproject.toml` 的 dev 依赖里声明了 `mutmut`，实际装到的是 `mutmut==3.8.0`。
3.x 版本改为把源码复制进 `mutants/` 目录再隔离执行 pytest，在本环境下 stats-collection
阶段的 pytest 子进程调用报错：

```
mutmut.runners.harness.BadTestExecutionCommandsException: Failed to run pytest with args:
['-q', '--rootdir=.', '--tb=native', '-x', '-q', '-p', 'no:randomly', '-p', 'no:random-order']
```

因此本演示采用**手动变异**（manual mutation）——这正是第 34 章"可验证清单"第 2 条、第 36.2 节
描述的变异测试思想的手动版："把被测实现故意改错，看测试红不红"。手动变异产出的 pytest 输出
真实可复现，不依赖 mutmut 的隔离机制。若将来升级到可用的 mutmut（或改用 cosmic-ray），
`setup.cfg` 里的 `source_paths=app/domain/invitation.py` 即为切入点。

---

## 第一步：一个弱断言的假测试（覆盖率有、断言无）

`tests/unit/test_is_expired.py` 最初写成这样（**本演示的"假测试"**）：

```python
def test_is_expired_weak() -> None:
    # 弱断言：只断言返回值不是 None（恒真），测不到任何边界行为。
    inv = _make(timedelta(days=1))
    result = inv.is_expired(utcnow())
    assert result is not None
```

这个测试"覆盖"了 `is_expired` 这一行，覆盖率报告会显示它被执行过。但它的断言
`result is not None` 对一个返回 `bool` 的函数**恒为真**——无论 `is_expired` 返回 True 还是
False 都通过。它是第 23.2 讲的"造假形态一：弱断言"。

对原始代码运行，它是绿的（baseline）：

```text
$ uv run pytest tests/unit/test_is_expired.py -v
========================= 1 passed, 1 warning in 0.01s =========================
```

## 第二步：注入变异，观察假测试没红（变异存活）

把 `is_expired` 的边界运算符从 `>=` 改成 `>`（这是 mutmut 会自动做的一类变异）：

```diff
- return now >= self.expires_at
+ return now > self.expires_at  # MUTANT: >= -> >
```

对**变异后的代码**再跑那个弱断言测试：

```text
$ uv run pytest tests/unit/test_is_expired.py -v
========================= 1 passed, 1 warning in 0.01s =========================
```

**测试依然全绿——变异存活。** 这证明：没有任何测试在验证 `now == expires_at` 这个边界的
行为。覆盖率发现不了这个（那一行确实被执行了），只有变异测试/手动变异能照出来（第 23.1/23.2）。

## 第三步：按需求补强断言，杀死变异体

依据 REQ-INV-006 的边界语义（恰好到期即过期），把断言钉死到三点行为：

```python
def test_is_expired_boundary() -> None:
    # 强断言：钉住 >= 的三点行为（来自 REQ-INV-006 的"7 天后过期"语义）。
    now = utcnow()
    inv = _make(timedelta(days=1))

    # 1) 过期时刻之前：未过期。
    assert inv.is_expired(now) is False
    # 2) 恰好等于 expires_at（边界）：按 >= 语义应判为已过期。
    assert inv.is_expired(inv.expires_at) is True
    # 3) 过期时刻之后：已过期。
    assert inv.is_expired(inv.expires_at + timedelta(seconds=1)) is True
```

对**仍然变异（`>`）的代码**跑补强后的测试——这次它红了，变异被杀死：

```text
$ uv run pytest tests/unit/test_is_expired.py::test_is_expired_boundary -v
    def test_is_expired_boundary() -> None:
        assert inv.is_expired(now) is False
>       assert inv.is_expired(inv.expires_at) is True
E       AssertionError: assert False is True
FAILED tests/unit/test_is_expired.py::test_is_expired_boundary - AssertionError
```

第 2 条断言 `inv.is_expired(inv.expires_at) is True` 精确命中边界：`>` 让"恰好到期"返回
False，于是测试红。这就是变异测试要的信号——**测试真的在验证边界行为了。**

## 第四步：恢复正确实现，补强测试转绿

把实现恢复为正确的 `>=`：

```text
$ uv run pytest tests/unit/test_is_expired.py -v
========================= 1 passed, 1 warning in 0.01s =========================
```

补强后的测试在正确实现上通过，在变异实现上失败——它成了一个**真正的验证器**。

---

## 复现步骤

```bash
cd backend
# 0) baseline：弱测试在原始代码上绿
uv run pytest tests/unit/test_is_expired.py -v
# 1) 手动变异：把 app/domain/invitation.py 里 `now >= self.expires_at` 改成 `now > self.expires_at`
# 2) 弱断言版（assert ... is not None）仍绿 -> 变异存活
# 3) 换成 test_is_expired_boundary 的三点强断言 -> 变异后代码红（变异被杀死）
# 4) 恢复 >=，强断言测试转绿
```

## 结论（呼应第 23/36 章）

- **覆盖率 ≠ 质量**：弱断言测试覆盖了那一行，却验证不了它的行为。
- **变异测试是照妖镜**：`>=`→`>` 的变异揭穿了假测试。
- **断言强度要成对设防**：补强断言的依据来自需求（REQ-INV-006），不是"让变异得分变好看"。
  这正是第 36.2 节强调的——不能让 agent 用"补一个恰好覆盖该行的假测试"去满足"消灭变异"
  这个新指标；修复必须回到需求定义的具体期望值。
