# Small official Python image
FROM python:3.13-slim

# Grab the uv binary, a fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy only the lockfiles first so this layer gets cached between builds
COPY pyproject.toml uv.lock ./

# Install the exact pinned versions from uv.lock
RUN uv sync --frozen --no-dev

# Copy this service's code, prompts live inside it already
COPY 03_python_orchestration ./03_python_orchestration

# Deployment runs uvicorn directly against the app object
# This skips main.py's own entrypoint, which is untouched for the course platform
EXPOSE 10002
ENV PORT=10002

CMD ["sh", "-c", "uv run uvicorn app.main:app --app-dir 03_python_orchestration --host 0.0.0.0 --port $PORT"]
