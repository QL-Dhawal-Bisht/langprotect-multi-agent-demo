"""Statically discoverable OpenAI Agents SDK topology for LangProtect.

LangProtect parses this file with Python AST and never imports it. Tool bodies are
deliberately inert
in case a developer imports the module manually. The live demo API is implemented separately in
`app.main` and does not load this module or call an LLM.
"""

from agents import Agent, ShellTool, WebSearchTool, function_tool, handoff
from agents.mcp import MCPServerSse, MCPServerStdio


@function_tool
def lookup_order(order_id: str) -> str:
    """Return synthetic order data only."""
    return f"SIMULATED order {order_id}"


@function_tool
def fetch_url(url: str) -> str:
    """Represent network access without making a request."""
    return f"SIMULATED fetch blocked for {url}"


@function_tool
def run_shell(command: str) -> str:
    """Represent command execution without executing anything."""
    return f"SIMULATED shell blocked for {command}"


@function_tool
def query_customer_database(query: str) -> str:
    """Represent read-only data access with no database connection."""
    return f"SIMULATED query blocked for {query}"


@function_tool
def send_email(recipient: str, subject: str) -> str:
    """Represent messaging without contacting a recipient."""
    return f"SIMULATED email blocked for {recipient}: {subject}"


@function_tool
def read_secret_token(secret_name: str) -> str:
    """Represent secret access without reading any secret."""
    return f"SIMULATED secret blocked for {secret_name}"


@function_tool
def write_report_file(path: str, content: str) -> str:
    """Represent filesystem write access without writing a file."""
    return f"SIMULATED write blocked for {path} ({len(content)} chars)"


@function_tool
def deploy_release(environment: str, version: str) -> str:
    """Represent deployment privileges without deploying anything."""
    return f"SIMULATED deployment blocked for {environment}@{version}"


local_operations_mcp = MCPServerStdio(
    name="Local Operations MCP",
    params={"command": "python", "args": ["-m", "demo_mcp"]},
)
crm_stream_mcp = MCPServerSse(
    name="CRM Stream MCP",
    url="https://example.invalid/mcp",
)

compliance_agent = Agent(
    name="Compliance Agent",
    instructions="Review policy and release operations using synthetic demo data only.",
    model="gpt-4.1-mini",
    tools=[read_secret_token, write_report_file, deploy_release],
    mcp_servers=[local_operations_mcp],
)

billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle synthetic billing requests and delegate policy review.",
    model="gpt-4.1-mini",
    tools=[query_customer_database, send_email, compliance_agent.as_tool()],
    handoffs=[handoff(agent=compliance_agent)],
    mcp_servers=[crm_stream_mcp],
)

support_agent = Agent(
    name="Support Agent",
    instructions="Route synthetic customer support requests to specialist agents.",
    model="gpt-4.1-mini",
    tools=[
        lookup_order,
        fetch_url,
        run_shell,
        WebSearchTool(),
        ShellTool(),
        billing_agent.as_tool(),
    ],
    handoffs=[handoff(agent=billing_agent)],
)
