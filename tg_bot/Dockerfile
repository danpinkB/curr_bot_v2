FROM python:3.10.12
# Or any preferred Python version.
WORKDIR .
COPY . ./
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system


CMD ["python", "__main__.py"]