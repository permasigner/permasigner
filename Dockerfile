FROM python:3.10.0-slim-bullseye
WORKDIR /permasigner

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# system dependencies
RUN apt-get update \
    && apt-get install -y git gcc python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /permasigner

# python dependencies
RUN pip install --upgrade pip setuptools wheel \
  && pip install -r requirements.txt
  
COPY . /permasigner

# git version
RUN echo "$(git rev-parse --abbrev-ref HEAD)"_"$(git rev-parse --short HEAD)" >> githash \
  && rm -rf .git

ENV IS_DOCKER_CONTAINER Yes 

ENTRYPOINT [ "permasigner/data/docker-entrypoint.sh" ]
