# ---- Node Stage ----

FROM python:3.10.12

ENV VAR1=10
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install & use pipenv
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system

WORKDIR /app

COPY src /app/src
#COPY ./cli /app/cli
# Creates a non-root user and adds permission to access the /app folder
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

ENV PYTHONPATH=/app
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "./src/__main__.py"]