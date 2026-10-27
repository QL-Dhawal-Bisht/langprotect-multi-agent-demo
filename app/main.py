"""FastAPI target for LangProtect baseline and graph-driven campaign demonstrations."""

from fastapi import FastAPI

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "deterministic-safe-demo"}


@app.get("/v1/architecture", response_model=ArchitectureResponse)
def get_architecture() -> ArchitectureResponse:
    return architecture()


@app.post("/v1/chat", response_model=ChatResponse)
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
