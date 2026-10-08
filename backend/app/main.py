"""应用入口。create_app() 组装 FastAPI 实例。"""

from __future__ import annotations

from fastapi import FastAPI

from app.api import invitations


def create_app() -> FastAPI:
    app = FastAPI(title="TeamPulse Invitations API", version="1.0.0")
    app.include_router(invitations.router)
    return app


app = create_app()
