from __future__ import annotations

import httpx

from backend.config import settings


class LLMError(Exception):
    pass


async def generate_text(prompt: str, temperature: float = 0.2, max_tokens: int = 256) -> str:
    if settings.mock_mode:
        return f"[MOCK RESPONSE] You asked: {prompt}"

    headers = {
        'Authorization': f'Bearer {settings.vllm_api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': settings.vllm_model,
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': temperature,
        'max_tokens': max_tokens,
    }

    url = f"{settings.vllm_base_url.rstrip('/')}/chat/completions"

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(f'Failed to call vLLM endpoint: {exc}') from exc

    data = response.json()
    try:
        return data['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError('Invalid response schema from vLLM endpoint') from exc
