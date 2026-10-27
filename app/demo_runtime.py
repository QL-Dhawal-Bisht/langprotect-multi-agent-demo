"""Safe deterministic behavior for the live Promptfoo target.

This module performs no LLM calls, shell commands, network requests, database access, messaging, or
file writes. Sensitive-looking actions are represented only as simulation events.
"""

import os
import uuid
from dataclasses import dataclass

from app.schemas import ArchitectureEdge, ArchitectureNode, ArchitectureResponse, SimulatedEvent

CANDIDATE_MARKER = os.getenv("DEMO_CANDIDATE_MARKER", "LANGPROTECT-DEMO-CANDIDATE")


@dataclass(frozen=True, slots=True)
class DemoResult:
    reply: str
    routed_agent: str
    candidate_signal: bool
    events: list[SimulatedEvent]


TRIGGER_TERMS = (
    "developer mode",
    "ignore all previous",
    "system prompt",
    "hidden configuration",
    "credentials",
    "api keys",
    "run_shell",
    "code execution",
    "query_customer_database",
    "read_secret_token",
    "send_email",
    "write_report_file",
    "deploy_release",
    "fetch_url",
)


def evaluate(message: str) -> DemoResult:
    """Return a deterministic simulated response suitable for bounded security testing."""
    lowered = message.lower()
    if any(term in lowered for term in ("invoice", "billing", "customer database")):
        agent = "Billing Agent"
    elif any(term in lowered for term in ("policy", "compliance", "deploy", "report")):
        agent = "Compliance Agent"
    else:
        agent = "Support Agent"

    candidate = any(term in lowered for term in TRIGGER_TERMS)
    events = [
        SimulatedEvent(
            agent=agent,
            action="evaluate_security_test_input",
            target="deterministic_demo_policy",
        )
    ]
    if candidate:
        reply = (
            f"{CANDIDATE_MARKER}: simulated policy bypass signal from {agent}. "
            "No tool, external system, or real-world effect was invoked."
        )
    else:
        reply = (
            f"{agent} handled the request safely. This deterministic demo performs no external "
            "actions."
        )
    return DemoResult(reply=reply, routed_agent=agent, candidate_signal=candidate, events=events)


def session_id(value: str | None) -> str:
    return value or f"demo-{uuid.uuid4()}"


def architecture() -> ArchitectureResponse:
    nodes = [
        ArchitectureNode(name="Support Agent", kind="agent"),
        ArchitectureNode(name="Billing Agent", kind="agent"),
        ArchitectureNode(name="Compliance Agent", kind="agent"),
        ArchitectureNode(name="run_shell", kind="tool"),
        ArchitectureNode(name="fetch_url", kind="tool"),
        ArchitectureNode(name="query_customer_database", kind="tool"),
        ArchitectureNode(name="read_secret_token", kind="tool"),
        ArchitectureNode(name="send_email", kind="tool"),
        ArchitectureNode(name="write_report_file", kind="tool"),
        ArchitectureNode(name="deploy_release", kind="tool"),
        ArchitectureNode(name="Local Operations MCP", kind="mcp_server"),
        ArchitectureNode(name="CRM Stream MCP", kind="mcp_server"),
    ]
    edges = [
        ArchitectureEdge(source="Support Agent", target="Billing Agent", relationship="handoff_to"),
        ArchitectureEdge(
            source="Support Agent", target="Billing Agent", relationship="uses_agent_as_tool"
        ),
        ArchitectureEdge(
            source="Billing Agent", target="Compliance Agent", relationship="handoff_to"
        ),
        ArchitectureEdge(
            source="Billing Agent", target="Compliance Agent", relationship="uses_agent_as_tool"
        ),
        ArchitectureEdge(source="Support Agent", target="run_shell", relationship="uses_tool"),
        ArchitectureEdge(source="Support Agent", target="fetch_url", relationship="uses_tool"),
        ArchitectureEdge(
            source="Billing Agent", target="query_customer_database", relationship="uses_tool"
        ),
        ArchitectureEdge(source="Billing Agent", target="send_email", relationship="uses_tool"),
        ArchitectureEdge(
            source="Compliance Agent", target="read_secret_token", relationship="uses_tool"
        ),
        ArchitectureEdge(
            source="Compliance Agent", target="write_report_file", relationship="uses_tool"
        ),
        ArchitectureEdge(
            source="Compliance Agent", target="deploy_release", relationship="uses_tool"
        ),
        ArchitectureEdge(
            source="Compliance Agent",
            target="Local Operations MCP",
            relationship="uses_mcp_server",
        ),
        ArchitectureEdge(
            source="Billing Agent", target="CRM Stream MCP", relationship="uses_mcp_server"
        ),
    ]
    return ArchitectureResponse(
        notice=(
            "Declared demo topology. LangProtect independently derives its evidence-backed graph "
            "from app/agent_graph.py."
        ),
        nodes=nodes,
        edges=edges,
    )
