# Demo Architecture

This repository is a safe, deterministic integration fixture for LangProtect. It separates static
architecture evidence from live target behavior.

## Static topology

`app/agent_graph.py` declares OpenAI Agents SDK patterns that LangProtect recognizes through AST
analysis. The file is never imported by the demo API.

```text
Support Agent (entry point)
  ├─ tools: lookup_order, fetch_url, run_shell, WebSearchTool, ShellTool
  ├─ handoff -> Billing Agent
  └─ agent-as-tool -> Billing Agent

Billing Agent
  ├─ tools: query_customer_database, send_email
  ├─ MCP -> CRM Stream MCP
  ├─ handoff -> Compliance Agent
  └─ agent-as-tool -> Compliance Agent

Compliance Agent
  ├─ tools: read_secret_token, write_report_file, deploy_release
  └─ MCP -> Local Operations MCP
```

This should produce evidence-backed hypotheses across code execution, network access, data-store,
messaging, identity/secret, filesystem-write, deployment, and MCP capability classes.

## Runtime boundary

`app/main.py` exposes the live test target. `app/demo_runtime.py` returns deterministic simulated
responses. It performs no LLM calls, shell execution, network fetches, database queries, secret
reads, messaging, file writes, or deployments.

A matching marker is a `candidate_success` only. It is never proof of exploitation or real-world
impact.
