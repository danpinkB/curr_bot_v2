FROM smart_router as r_image
FROM nikolaik/python-nodejs:python3.10-nodejs18-alpine
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