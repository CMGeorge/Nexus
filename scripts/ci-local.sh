#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Nexus — Local CI Runner
# ─────────────────────────────────────────────────────────────
# Simulates GitHub Actions workflow locally using 'act'.
# Requires: brew install act (or https://github.com/nektos/act)
#
# Usage:
#   ./scripts/ci-local.sh              # Run e2e workflow
#   ./scripts/ci-local.sh --dry-run     # Show what would run
#   ./scripts/ci-local.sh --job e2e     # Run specific job
# ─────────────────────────────────────────────────────────────
set -euo pipefail

cd "$(dirname "$0")/.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Nexus Local CI ===${NC}"

# ── Check prerequisites ──
if ! command -v act &>/dev/null; then
    echo -e "${RED}ERROR: 'act' is not installed.${NC}"
    echo "Install: brew install act"
    echo "Or visit: https://github.com/nektos/act"
    exit 1
fi

if ! command -v docker &>/dev/null; then
    echo -e "${RED}ERROR: Docker is not running.${NC}"
    echo "Start Docker Desktop and retry."
    exit 1
fi

# ── Run workflows ──
JOB="${1:-}"
EXTRA_ARGS=""

if [ "$JOB" = "--dry-run" ]; then
    echo -e "${YELLOW}Dry-run mode — listing workflows...${NC}"
    act -l
    exit 0
fi

if [ -n "$JOB" ]; then
    EXTRA_ARGS="-j $JOB"
    echo -e "${GREEN}Running job: $JOB${NC}"
else
    echo -e "${GREEN}Running full e2e workflow...${NC}"
fi

# Run act with medium-sized runner (closer to GitHub ubuntu-latest)
# Auto-detect Apple Silicon and set architecture
ARCH_FLAG=""
if [[ "$(uname -m)" == "arm64" ]]; then
    ARCH_FLAG="--container-architecture linux/amd64"
fi

act push \
    $ARCH_FLAG \
    --platform ubuntu-latest=catthehacker/ubuntu:full-latest \
    --artifact-server-path /tmp/act-artifacts \
    $EXTRA_ARGS \
    "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}=== CI PASSED ===${NC}"
else
    echo -e "${RED}=== CI FAILED (exit $EXIT_CODE) ===${NC}"
    echo "Check artifacts: /tmp/act-artifacts"
fi

exit $EXIT_CODE