"""API contracts for the deterministic demo target."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    message: str | None = Field(default=None, min_length=1, max_length=8_000)
    prompt: str | None = Field(default=None, min_length=1, max_length=8_000)
    session_id: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def require_input(self) -> "ChatRequest":
        if self.message is None and self.prompt is None:
            raise ValueError("message or prompt is required")
        return self


class SimulatedEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    agent: str
    action: str
    target: str
    simulated: bool = True


class ChatResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    reply: str
    session_id: str
    routed_agent: str
    candidate_signal: bool
    effects_performed: bool = False
    events: list[SimulatedEvent]


class ArchitectureNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    kind: str


class ArchitectureEdge(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str
    target: str
    relationship: str


class ArchitectureResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    notice: str
    nodes: list[ArchitectureNode]
    edges: list[ArchitectureEdge]
