#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

UID_NUM=$(id -u)
R_PORT=$((10000 + (UID_NUM % 6000) * 3 + 0))
DATA_PORT=$((10000 + (UID_NUM % 6000) * 3 + 1))
ORCH_PORT=$((10000 + (UID_NUM % 6000) * 3 + 2))

PID_FILE=/tmp/apis-all-along.pids
: > "$PID_FILE"

Rscript 01_r_service/plumber.R > /tmp/apis-all-along-01-r-service.log 2>&1 &
echo $! >> "$PID_FILE"

uv run --directory 02_python_data_service python -m app.main \
  > /tmp/apis-all-along-02-python-data-service.log 2>&1 &
echo $! >> "$PID_FILE"

uv run --directory 03_python_orchestration python -m app.main \
  > /tmp/apis-all-along-03-python-orchestration.log 2>&1 &
echo $! >> "$PID_FILE"

echo "01_r_service:            http://localhost:$R_PORT"
echo "02_python_data_service:  http://localhost:$DATA_PORT"
echo "03_python_orchestration: http://localhost:$ORCH_PORT"
echo
echo "Logs: /tmp/apis-all-along-*.log"
echo "Stop: scripts/stop_all.sh"
