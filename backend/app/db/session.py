"""数据库引擎与会话工厂。

默认连 Postgres（TEAMPULSE_DATABASE_URL），测试里由 fixture 覆盖为 SQLite 内存库。
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_URL = "postgresql+psycopg://teampulse:teampulse@localhost:5432/teampulse"


def get_database_url() -> str:
    return os.environ.get("TEAMPULSE_DATABASE_URL", DEFAULT_URL)


def make_engine(url: str | None = None) -> Engine:
    return create_engine(url or get_database_url(), future=True)


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _ensure() -> sessionmaker[Session]:
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = make_engine()
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    return _SessionLocal


def get_session() -> Session:
    return _ensure()()
