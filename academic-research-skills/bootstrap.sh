#!/bin/sh
# Portable Python discovery only; never installs a system runtime with elevated privileges.
set -eu
BASE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c 'import sys; raise SystemExit(sys.version_info < (3,10))' 2>/dev/null; then
    exec "$PY" "$BASE/scripts/environment.py" "$@"
  fi
done
printf '%s\n' 'Python >=3.10 is required for executable setup. Ask the authorized host to install Python from the official source or system package manager. Text-only use needs no Python.' >&2
exit 3
