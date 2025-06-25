FROM --platform=linux/amd64 python:3.13.5-slim

# add new user
RUN groupadd -r web && useradd -r -g web web

# add uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# add nc (for entrypoint running)
RUN apt-get upgrade && apt-get update && apt-get install -y netcat-traditional

WORKDIR /app

# copy info about project dependencies
COPY uv.lock pyproject.toml .python-version /app

# install dependencies only, excluding dev dependencies
RUN uv sync --frozen --no-dev --no-install-project

COPY entrypoint.sh /app/
COPY . /app

# give execute right to all users
RUN chmod +x /app/entrypoint.sh

# create logs directory if not exists and set directory owner to "web" user
RUN mkdir -p /app/logs \
    && chown -R web:web logs

ENTRYPOINT ["/app/entrypoint.sh"]
