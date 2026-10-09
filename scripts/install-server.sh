#!/usr/bin/env bash
# Install our customizations into a xiaozhi-esp32-server checkout.
# Usage: scripts/install-server.sh [path/to/xiaozhi-esp32-server]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
XZ="${1:-$HOME/Documents/repos/xiaozhi-esp32-server}/main/xiaozhi-server"
IP="$(ipconfig getifaddr en0 || ipconfig getifaddr en1)"
[ -f "$XZ/app.py" ] || { echo "not a xiaozhi-server dir: $XZ" >&2; exit 1; }

# Plugin and provider are symlinked so edits in this repo take effect on restart.
ln -sfn "$REPO/server/plugins/get_weather_openmeteo.py" "$XZ/plugins_func/functions/get_weather_openmeteo.py"
ln -sfn "$REPO/server/providers/llm/openai_nothink" "$XZ/core/providers/llm/openai_nothink"

mkdir -p "$XZ/data"
sed "s/__LAN_IP__/$IP/g" "$REPO/server/config.yaml" > "$XZ/data/.config.yaml"
echo "Installed into $XZ (LAN IP $IP)"
