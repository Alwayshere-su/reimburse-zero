#!/usr/bin/env bash
set -euo pipefail

INSTALLER="${AGENTTEAMS_INSTALLER:-/tmp/install.sh}"
if [[ ! -f "$INSTALLER" ]]; then
  echo "AgentTeams installer not found: $INSTALLER" >&2
  echo "Download the official installer first, or set AGENTTEAMS_INSTALLER to its path." >&2
  exit 1
fi

echo "=== AgentTeams 安装器开始 ==="
echo "按安装器提示在本机配置模型与凭据；不要把任何 Key/Token 写入仓库。"
bash "$INSTALLER"
