FROM node:18-alpine as builder
WORKDIR .
COPY /other_builds/smart-order-router .
RUN npm install
RUN npm run build

FROM nikolaik/python-nodejs:python3.11-nodejs18-alpine
WORKDIR /docker_app
COPY --from=builder ./ /docker_app/cli/
RUN pip install --upgrade pip && pip install poetry
COPY ./poetry.lock ./pyproject.toml /docker_app/
RUN poetry install
ENTRYPOINT ["poetry", "run"]
ENV PYTHONPATH=/docker_app
ENV UNI_CLI_PATH=/docker_app/cli/
ENV PYTHONUNBUFFERED=1
COPY . /docker_app