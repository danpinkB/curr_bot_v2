FROM python:3.11-alpine

WORKDIR /docker_app

RUN apk add --update nodejs nodejs-npm

#COPY ./external_dependencies/smart-order-router /docker_app/

RUN npm install && npm run build

WORKDIR /docker_app
COPY --from=r_image /docker_app /docker_app/cli/
RUN pip install --upgrade pip && pip install poetry
COPY ./poetry.lock ./pyproject.toml /docker_app/
RUN poetry install
ENTRYPOINT ["poetry", "run"]
ENV PYTHONPATH=/docker_app
ENV UNI_CLI_PATH=/docker_app/cli/
ENV PYTHONUNBUFFERED=1
COPY . /docker_app