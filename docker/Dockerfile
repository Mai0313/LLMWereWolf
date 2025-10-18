ARG PYTHON_VERSION=3.10
FROM nikolaik/python-nodejs:python${PYTHON_VERSION}-nodejs22 AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL maintainer="Wei Lee <mai@mai0313.com>" \
    org.label-schema.name="repo_template" \
    org.label-schema.vendor="Wei Lee" \
    org.label-schema.schema-version="1.0" \
    com.centurylinklabs.watchtower.stop-signal="SIGINT"

########################################################################################

FROM builder AS prod
WORKDIR /app
COPY . .
# RUN uv sync --frozen --no-dev && uv cache clean
RUN uv sync --no-dev && \
    uv cache clean
