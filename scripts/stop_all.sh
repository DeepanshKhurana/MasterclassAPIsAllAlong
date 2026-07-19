#!/bin/bash
set -uo pipefail

PID_FILE=/tmp/apis-all-along.pids

if [[ ! -f "$PID_FILE" ]]; then
  echo "No PID file found at $PID_FILE — nothing to stop (or already stopped)."
  exit 0
fi

while read -r pid; do
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    echo "Stopped PID $pid"
  fi
done < "$PID_FILE"

rm -f "$PID_FILE"
