FROM python:3.10.0-slim-bullseye 
WORKDIR /usr/src/permasigner

# system dependencies
RUN apt-get update
RUN apt-get upgrade -y
RUN apt install -y git gcc python3-dev

# python dependencies
COPY . .
RUN pip install --upgrade pip setuptools wheel poetry
RUN poetry install

ENV IS_DOCKER_CONTAINER Yes
ENTRYPOINT [ "data/docker-entrypoint.sh" ]