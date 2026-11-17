from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.config import settings
from backend.llm_client import LLMError, generate_text


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=2048)


class ChatResponse(BaseModel):
    answer: str
    model: str
    mock_mode: bool


app = FastAPI(title='GenAI Backend (FastAPI + vLLM)', version='1.0.0')


@app.get('/health')
def health() -> dict:
    return {
        'status': 'ok',
        'env': settings.app_env,
        'mock_mode': settings.mock_mode,
        'model': settings.vllm_model,
    }


@app.post('/chat', response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        answer = await generate_text(
            prompt=req.prompt,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
        return ChatResponse(answer=answer, model=settings.vllm_model, mock_mode=settings.mock_mode)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
