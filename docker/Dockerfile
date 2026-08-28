FROM nikolaik/python-nodejs:python3.10-nodejs22 AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=ghcr.io/astral-sh/ty:latest /ty /bin/

LABEL maintainer="Wei Lee <mai@mai0313.com>" \
    org.label-schema.name="llm_werewolf" \
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
