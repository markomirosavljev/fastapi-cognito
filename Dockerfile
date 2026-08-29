FROM python:3.12-alpine AS base

ENV UV_PROJECT_ENVIRONMENT="/opt/pysetup/.venv" \
    PYSETUP_PATH=/opt/pysetup \
    VENV_PATH=/opt/pysetup/.venv

ENV PATH="$PATH:$VENV_PATH/bin"

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR $PYSETUP_PATH

COPY README.md pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --group test

FROM base AS run

COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

COPY test /app/test

WORKDIR /app

CMD [ "pytest", "-s" ]
