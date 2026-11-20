#!/usr/bin/env bash
# Run via: bash scripts/codex-cloud-setup.sh
# Installs existing lockfile-pinned dependencies in a Codex Cloud environment.
# Never pass live production secrets to setup.
set -euo pipefail

cd "$(dirname "$0")/.."
echo "Evalio Codex Cloud setup"
node --version
npm --version
python3 --version
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Configure uv in the cloud environment image before running." >&2
  exit 1
fi
uv --version

# Use lockfile-resolved dependency graph; do not mutate lockfiles during setup.
npm ci
uv sync --frozen
echo "Ready: use existing npm/uv test scripts for task-specific validation."
