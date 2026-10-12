# shop/api/__init__.py —— 顶层，依赖 service（向下，合法）
from shop.service import user_profile

def handle(uid: int) -> dict:
    return {"ok": True, "data": user_profile(uid)}
