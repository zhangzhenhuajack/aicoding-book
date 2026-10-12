"""token 生成与哈希。

明文 token 用 secrets.token_urlsafe(32) 生成，只在创建响应里返回一次；
服务端只保存其 SHA-256 十六进制摘要（REQ-INV-005）。查询邀请时用哈希比对，
使"token 是否存在"不改变数据库查询路径（REQ-INV-011）。
"""

from __future__ import annotations

import hashlib
import secrets


def generate_token() -> str:
    """生成一次性明文邀请 token。"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """对 token 做 SHA-256，返回十六进制摘要。"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
