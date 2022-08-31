FROM python:3.10.6-bullseye AS venv

WORKDIR /app
COPY requirements.txt ./
RUN python3 -m venv --copies /app/venv

RUN . /app/venv/bin/activate \
    && python3 -m pip install --no-cache-dir --upgrade pip setuptools \
    && python3 -m pip install --no-cache-dir -r requirements.txt


FROM alpine/git:2.36.2 AS git
ADD .git /app
WORKDIR /app
RUN echo "$(git rev-parse --abbrev-ref HEAD)"_"$(git rev-parse --short HEAD)" >> /version


FROM python:3.10.6-slim-bullseye AS main

COPY --from=venv /app/venv /app/venv/
ENV PATH /app/venv/bin:$PATH

WORKDIR /app
COPY docker ./docker/
COPY main.py LICENSE ./
COPY permasigner ./permasigner/
COPY --from=git /version /app/.version


ENV IS_DOCKER_CONTAINER Yes

CMD [ "/app/docker/entrypoint.sh" ]
