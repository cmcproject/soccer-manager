FROM python:3.10-alpine3.18
LABEL maintainer="marius.crisan.tech@gmail.com"

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.4.2

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

COPY . /code
WORKDIR /code/src

EXPOSE 8000

ARG DEV=false
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-interaction --no-ansi

RUN if [ $DEV = "true" ]; then \
        poetry install --only=dev --no-interaction --no-ansi; \
    fi

RUN adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

USER django-user