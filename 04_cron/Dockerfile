# Small official Python image
FROM python:3.13-slim

# Grab the uv binary, a fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy only the lockfiles first so this layer gets cached between builds
COPY pyproject.toml uv.lock ./

# Install the exact pinned versions from uv.lock
RUN uv sync --frozen --no-dev

# Copy this job's code
COPY 04_cron ./04_cron

# Render runs this once per schedule, then the container exits
CMD ["uv", "run", "python", "04_cron/warm_services.py"]
