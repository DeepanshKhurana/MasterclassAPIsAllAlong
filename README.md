# APIs All Along

[![AI-DECLARATION: pair](https://img.shields.io/badge/䷼%20AI--DECLARATION-pair-ffedd5?labelColor=ffedd5)](https://ai-declaration.md)

[Slides](https://docs.google.com/presentation/d/1jrrvZZWFT5cSKzvnGO3VhTEudldvExpwyX0tRG4JZE8/)

R and Python working together on cricket data. Three small services, meant
to be explored one at a time, in order:

1. `01_r_service` (R, Plumber2, cricketdata). Pulls official team stats from
   ESPNcricinfo.
2. `02_python_data_service` (Python, FastAPI, cricketstats). Computes its own
   team stats from raw ball by ball data.
3. `03_python_orchestration` (Python, FastAPI, LangChain, OpenRouter). Calls
   both services above and turns the combined result into a plain English
   answer.

Each folder can be opened and understood on its own before moving to the next.

## Prerequisites

- R 4.4 or newer, with renv
- Python 3.13, with uv
- An OpenRouter API key (only needed for the LLM endpoints in
  `03_python_orchestration`)

## Setup

```bash
Rscript -e 'install.packages("renv")' -e 'renv::restore()'
uv sync
cp .env.example .env
```

Add your OpenRouter key to `.env` once you get to step 3.

To confirm every pinned package actually loads, without starting any servers:

```bash
Rscript scripts/check_r_packages.R
uv run python scripts/check_python_packages.py
```

## Run everything

```bash
scripts/run_all.sh
```

This starts all three services and prints the port each one is running on.
Ports are derived from your user id, so this also works if several people
share one machine. Stop them with:

```bash
scripts/stop_all.sh
```

To run a single service on its own instead, see the README (or the plumber /
main file) inside that service's folder.

## Try it

See [EXAMPLES.md](EXAMPLES.md) for five ready to run example queries.

## What's in this repo

- `01_r_service`, `02_python_data_service`, `03_python_orchestration`. The
  three services, numbered in the order they build on each other.
- `03_python_orchestration/prompts`. The LLM prompt templates. Edit these
  freely, no restart needed.
- `scripts`. Start everything, stop everything, and check that packages are
  installed.
- `config.yml`, `renv.lock`, `pyproject.toml`, `uv.lock`. Setup files used by
  `renv`, `uv`, and the AthlyticZ platform. You will not need to open these
  to understand the project.
- `docker-compose.yml`. Runs all three services together in Docker, for
  general deployment on any VM or host.
- `render.yaml`. A Render Blueprint for deploying the same services plus the
  `04_cron` warm up job on Render specifically.
