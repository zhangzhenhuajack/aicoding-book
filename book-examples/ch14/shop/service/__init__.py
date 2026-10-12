# shop/service/__init__.py —— 中层，依赖 repo（向下，合法）
from shop.repo import get_user

def user_profile(uid: int) -> dict:
    u = get_user(uid)
    return {"profile": u["name"]}
