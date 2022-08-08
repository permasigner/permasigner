FROM python:3.10.0-slim-bullseye
WORKDIR /permasigner

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /permasigner

# python dependencies
RUN deps='gcc python3-dev' \
    && set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install --no-install-recommends -y $deps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge --auto-remove -y $deps


COPY . /permasigner

# git dependency
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install --no-install-recommends -y git \
    && echo "$(git rev-parse --abbrev-ref HEAD)"_"$(git rev-parse --short HEAD)" >> githash \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge --auto-remove -y git \
    && rm -rf .git

ENV IS_DOCKER_CONTAINER Yes
ENTRYPOINT [ "permasigner/data/docker-entrypoint.sh" ]

