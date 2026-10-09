#!/usr/bin/env bash
# Start Piper TTS (127.0.0.1:5000) and xiaozhi-esp32-server (ws :8000, http :8003).
# Assumes Ollama is already up (scripts/start-ollama.sh). Ctrl-C stops both.
set -euo pipefail
XZ="${XZ:-$HOME/Documents/repos/xiaozhi-esp32-server}/main/xiaozhi-server"
cd "$XZ"
PY=.venv/bin/python
# python.org Python ships without a CA bundle; use certifi's.
export SSL_CERT_FILE="$($PY -m certifi)"
# Native Homebrew first: ffmpeg is required at startup.
export PATH="/opt/homebrew/bin:$PATH"
# opuslib needs native (arm64) libopus from /opt/homebrew.
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"

$PY -m piper.http_server --data-dir data/piper -m en_US-lessac-medium --host 127.0.0.1 --port 5000 >tmp/piper.log 2>&1 &
PIPER=$!
trap 'kill $PIPER 2>/dev/null' EXIT
for _ in $(seq 1 40); do curl -sf -o /dev/null -X POST -H 'Content-Type: application/json' -d '{"text":"ok"}' http://127.0.0.1:5000/synthesize && break; sleep 0.5; done

$PY app.py
