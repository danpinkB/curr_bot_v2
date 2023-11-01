FROM python:3.11-alpine3.18

RUN apk update \
    && apk add --no-cache make gcc libffi-dev musl-dev build-base mpc1-dev g++ gcc gpgme-dev libc-dev bash nodejs npm \
    && pip install --upgrade pip \
    && pip install poetry

WORKDIR /docker_app

COPY ./vendor/smart-order-router /docker_app/vendor/smart-order-router

RUN cd /docker_app/vendor/smart-order-router && npm ci && npm run build

COPY ./poetry.lock ./pyproject.toml /docker_app/
RUN poetry install

ENTRYPOINT ["poetry", "run"]
ENV PYTHONPATH=/docker_app
ENV UNI_CLI_PATH=/docker_app/vendor/smart-order-router
ENV PYTHONUNBUFFERED=1
COPY . /docker_app
