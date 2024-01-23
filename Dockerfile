FROM python:3.11-alpine
# Or any preferred Python version.
WORKDIR /docker_app
RUN pip install --upgrade pip && pip install poetry
COPY ./poetry.lock ./pyproject.toml /docker_app/
RUN poetry install
ENTRYPOINT ["poetry", "run"]
ENV PYTHONPATH=/docker_app
ENV PYTHONUNBUFFERED=1
COPY . /docker_app