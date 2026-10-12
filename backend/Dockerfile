# syntax=docker/dockerfile:1
# 多阶段构建：builder 用 uv 装依赖到 .venv，runtime 只带运行时 + 非 root 用户。

FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app
# 先只拷依赖清单，利用层缓存
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
# 再拷源码并安装项目本身
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime
# 非 root 运行
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
