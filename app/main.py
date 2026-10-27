"""FastAPI target for LangProtect baseline and graph-driven campaign demonstrations."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.demo_runtime import architecture, evaluate_with_provider, provider_name, session_id
from app.schemas import ArchitectureResponse, ChatRequest, ChatResponse

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="LangProtect Multi-Agent Demo",
    version="0.2.0",
    description=(
        "Safe provider-backed target for authorized LangProtect testing. It simulates candidate "
        "signals and never performs real tool side effects."
    ),
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False, response_class=FileResponse)
def agent_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "safe-demo", "provider": provider_name()}


@app.get("/v1/architecture", response_model=ArchitectureResponse)
def get_architecture() -> ArchitectureResponse:
    return architecture()


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    result = await evaluate_with_provider(payload.message or payload.prompt or "")
    return ChatResponse(
        reply=result.reply,
        session_id=session_id(payload.session_id),
        routed_agent=result.routed_agent,
        provider=result.provider,
        candidate_signal=result.candidate_signal,
        effects_performed=False,
        events=result.events,
    )
