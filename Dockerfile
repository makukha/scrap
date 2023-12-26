# sync with .python-version and pyproject.toml
FROM python:3.11.7-slim-bullseye as base

SHELL ["/bin/bash", "-eux", "-o", "pipefail", "-c"]

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /home/build


FROM base as build

RUN pip install poetry
COPY poetry.lock pyproject.toml ./

COPY src/ ./src
RUN poetry build --no-interaction
