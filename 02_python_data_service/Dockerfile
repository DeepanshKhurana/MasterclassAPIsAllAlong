# Small official Python image
FROM python:3.13-slim

# Grab the uv binary, a fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy only the lockfiles first so this layer gets cached between builds
COPY pyproject.toml uv.lock ./

# Install the exact pinned versions from uv.lock
RUN uv sync --frozen --no-dev

# Copy this service's code
COPY 02_python_data_service ./02_python_data_service

# Deployment runs uvicorn directly against the app object
# This skips main.py's own entrypoint, which is untouched for the course platform
EXPOSE 10001
ENV PORT=10001

CMD ["sh", "-c", "uv run uvicorn app.main:app --app-dir 02_python_data_service --host 0.0.0.0 --port $PORT"]
