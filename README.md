# ESP32 Voice Assistant (experimental)

Local voice assistant on a Waveshare ESP32-S3-AUDIO-Board talking to a local LLM (Ollama, `qwen3:8b`) on a Mac.
This is a trial run while we wait for a dedicated LLM server. What we learn here will shape the real setup.

## Part 1 – Voice weather query
Board (XiaoZhi firmware) → xiaozhi-esp32-server on the Mac (local STT → Ollama → local TTS) → board.
A `get_weather(location?)` tool uses Open-Meteo and defaults to **Nampa, ID** when you don't name a place.

## Part 2 – Claude controls the local LLM
A small `local-llm` MCP server (`ask_local`, `list_models`) lets Claude Code hand off small tasks to Ollama.

## Plan
Full plan: [ESP32 Voice Assistant – Experimental Plan](https://docs.google.com/document/d/1LKtFHFKGZtDtuS5XtwG7OU1HQpyIoBrRifobBde8CZw/edit)

## License
Public domain ([The Unlicense](LICENSE)).
