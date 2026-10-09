#!/usr/bin/env bash
# Start Ollama listening on the LAN and smoke-test the OpenAI-compatible endpoint.
# Usage: scripts/start-ollama.sh [model]   (default qwen3:8b)
set -euo pipefail
MODEL="${1:-qwen3:8b}"
IP="$(ipconfig getifaddr en0 || ipconfig getifaddr en1)"
LOG="${TMPDIR:-/tmp}/ollama-lan.log"

if ! lsof -nP -iTCP:11434 -sTCP:LISTEN >/dev/null 2>&1; then
  OLLAMA_HOST=0.0.0.0:11434 OLLAMA_KEEP_ALIVE=-1 nohup ollama serve >"$LOG" 2>&1 &
  for _ in $(seq 1 40); do curl -sf "http://$IP:11434/api/version" >/dev/null && break; sleep 0.5; done
fi

echo "Ollama on http://$IP:11434/v1 (log: $LOG)"
# qwen3 ignores "/no_think" via /v1; reasoning_effort=none disables thinking (~3s vs ~45s).
curl -sS -w '\nHTTP %{http_code} in %{time_total}s\n' "http://$IP:11434/v1/chat/completions" \
  -H 'Content-Type: application/json' \
  -d "{\"model\":\"$MODEL\",\"reasoning_effort\":\"none\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hi in 3 words.\"}]}"

# Firewall: the allow rule is tied to the versioned Cellar path; re-check after brew upgrade.
/usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep -A1 -i ollama || \
  echo "WARN: no firewall rule for ollama; run: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add \"$(readlink -f "$(which ollama)")\""
