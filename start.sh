#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec python3 run.py --host "${ARYLIDE_HOST:-127.0.0.1}" --port "${ARYLIDE_PORT:-4173}"
