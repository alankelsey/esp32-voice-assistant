"""OpenAI-compatible LLM provider that always disables model "thinking".

Upstream's openai provider only disables thinking for a hard-coded list of cloud
domains, and its ollama provider relies on a "/no_think" prefix that qwen3 ignores
over Ollama's /v1 API. Ollama honors reasoning_effort="none" (~1-3s vs ~14s for a
short reply on an M4 Pro), which matters a lot for voice latency.
"""
from core.providers.llm.openai.openai import LLMProvider as OpenAILLMProvider


class LLMProvider(OpenAILLMProvider):
    def _apply_thinking_disabled(self, request_params: dict):
        request_params.setdefault("extra_body", {})["reasoning_effort"] = "none"
