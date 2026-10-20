#!/usr/bin/env bash
set -euo pipefail

: "${AGENTTEAMS_LLM_API_KEY:?set AGENTTEAMS_LLM_API_KEY before running}"

export AGENTTEAMS_NON_INTERACTIVE=1
export AGENTTEAMS_LANGUAGE=zh
export AGENTTEAMS_VERSION=latest
export AGENTTEAMS_LLM_PROVIDER=openai-compat
export AGENTTEAMS_DEFAULT_MODEL="${AGENTTEAMS_DEFAULT_MODEL:-deepseek-v4-flash}"
export AGENTTEAMS_OPENAI_BASE_URL="${AGENTTEAMS_OPENAI_BASE_URL:-https://api.deepseek.com/v1}"
export AGENTTEAMS_LLM_API_KEY
export AGENTTEAMS_MODEL_CONTEXT_WINDOW=1000000
export AGENTTEAMS_MODEL_MAX_TOKENS=384000
export AGENTTEAMS_MODEL_REASONING=true
export AGENTTEAMS_MODEL_VISION=false
export AGENTTEAMS_EMBEDDING_MODEL=""
export AGENTTEAMS_DEFAULT_WORKER_RUNTIME=copaw
export AGENTTEAMS_MANAGER_RUNTIME=copaw

INSTALLER="${AGENTTEAMS_INSTALLER:-/tmp/install.sh}"
if [[ ! -f "$INSTALLER" ]]; then
  echo "AgentTeams installer not found: $INSTALLER" >&2
  echo "Download it first, or set AGENTTEAMS_INSTALLER to its path." >&2
  exit 1
fi

echo "=== AgentTeams 非交互安装开始 ==="
bash "$INSTALLER"
