# `python-base` sets up all our shared environment variables
FROM python:3.10.6-slim-bullseye as base

    # python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.2.1 \
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/app" \
    VENV_PATH="/app/env"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# `builder` stage is used to build deps + create our virtual environment
FROM base as builder
RUN apt-get update && apt-get install --no-install-recommends -y curl

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY permasigner ./permasigner
COPY LICENSE README.md main.py ./
COPY pyproject.toml poetry.lock ./

# Build the permasigner
RUN poetry build --format wheel
RUN python -m venv env
RUN pip install dist/*.whl

### 2ND STAGE BUILD ###

FROM base as main

# copy in the virtual environment
COPY --from=builder $VENV_PATH $VENV_PATH

ENV IS_DOCKER_CONTAINER Yes

ENTRYPOINT [ "permasigner" ]
