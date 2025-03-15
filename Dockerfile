FROM python:3.12-alpine AS base

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYSETUP_PATH=/opt/pysetup \
    VENV_PATH=/opt/pysetup/.venv

ENV PATH="$PATH:$POETRY_HOME/bin:$VENV_PATH/bin"

FROM base AS builder

RUN apk add --update --no-cache curl 

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH

COPY README.md pyproject.toml poetry.lock ./
COPY src ./src

RUN poetry install --no-interaction --no-ansi --with test

FROM base AS run

COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

COPY test /app/test

WORKDIR /app

CMD [ "pytest", "-s" ]
