"""FastAPI target for LangProtect baseline and graph-driven campaign demonstrations."""

import hmac
import os

from fastapi import Depends, FastAPI, Header, HTTPException, status

from app.demo_runtime import architecture, evaluate, session_id
from app.schemas import ArchitectureResponse, ChatRequest, ChatResponse

app = FastAPI(
    title="LangProtect Multi-Agent Demo",
    version="0.1.0",
    description=(
        "Safe deterministic target for authorized LangProtect testing. It simulates candidate "
        "signals and never performs real tool side effects."
    ),
)


def require_api_key(x_demo_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("DEMO_API_KEY", "demo-only-key")
    if x_demo_api_key is None or not hmac.compare_digest(x_demo_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-Demo-API-Key header is required.",
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "deterministic-safe-demo"}


@app.get(
    "/v1/architecture",
    response_model=ArchitectureResponse,
    dependencies=[Depends(require_api_key)],
)
def get_architecture() -> ArchitectureResponse:
    return architecture()


@app.post(
    "/v1/chat",
    response_model=ChatResponse,
    dependencies=[Depends(require_api_key)],
)
def chat(payload: ChatRequest) -> ChatResponse:
    result = evaluate(payload.message or payload.prompt or "")
    return ChatResponse(
        reply=result.reply,
        session_id=session_id(payload.session_id),
        routed_agent=result.routed_agent,
        candidate_signal=result.candidate_signal,
        effects_performed=False,
        events=result.events,
    )
