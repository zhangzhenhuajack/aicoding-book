"""生成 Demo 32-1 的两套样例包（本书示例）：
app/     —— 故意带三类违规：orders↔billing 循环依赖、charge() 圈复杂度 13、legacy.py 被 90 个琐碎函数撑到 270 行
app_ok/  —— 修正版：去掉循环依赖、把 charge() 拆成小函数、legacy.py 瘦身到 30 行
用法：python3 make_samples.py
"""
from pathlib import Path

RULES = ["vip", "coupon", "bulk", "holiday", "member", "first_order",
         "referral", "flash_sale", "bundle", "clearance", "student", "senior"]


def write(path: str, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def legacy(n: int) -> str:
    return "".join(f"def helper_{i}():\n    value = {i}\n    return value\n\n" for i in range(n))


# ---------- 违规版 app/ ----------
charge = ["from app import orders", "", "def charge(order):", "    price = order['price']"]
for r in RULES:                                  # 12 个 if → 圈复杂度 1 + 12 = 13
    charge += [f"    if order.get('{r}'):", "        price *= 0.95"]
charge += ["    orders.mark_charged(order)", "    return price", ""]
write("app/billing.py", "\n".join(charge))
write("app/orders.py",
      "from app import billing\n\n\ndef mark_charged(order):\n    order['charged'] = True\n\n\n"
      "def place(order):\n    return billing.charge(order)\n")
write("app/legacy.py", legacy(90))              # 90 × 3 行 = 270 个非空行

# ---------- 修正版 app_ok/ ----------
write("app_ok/billing.py",
      "RULES = " + repr(RULES) + "\n\n\n"
      "def discount_rate(order):\n"
      "    hits = sum(1 for r in RULES if order.get(r))\n"
      "    return 0.95 ** hits\n\n\n"
      "def charge(order):\n"
      "    return order['price'] * discount_rate(order)\n")
write("app_ok/orders.py",                        # 只有 orders → billing 单向依赖
      "from app_ok import billing\n\n\ndef place(order):\n"
      "    order['charged'] = True\n    return billing.charge(order)\n")
write("app_ok/legacy.py", legacy(10))           # 瘦身到 30 行
print("已生成 app/ 与 app_ok/")
