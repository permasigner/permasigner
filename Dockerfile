FROM python:3.10.0-slim-bullseye 
WORKDIR /usr/src/permasigner

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# system dependencies
RUN apt-get update
RUN apt-get upgrade -y
RUN apt install -y git gcc python3-dev

# python dependencies
COPY ./requirements.txt .
COPY . .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

ENV IS_DOCKER_CONTAINER Yes
ENTRYPOINT [ "permasigner/data/docker-entrypoint.sh" ]
