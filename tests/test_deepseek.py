import asyncio

import httpx

from app.deepseek import DeepSeekClient, DeepSeekConfig, DeepSeekError


def test_deepseek_client_maps_chat_completion_without_leaking_marker() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-secret"
        assert request.url.path == "/chat/completions"
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Safe answer LANGPROTECT-DEMO-CANDIDATE"}}]},
        )

    async def run() -> str:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            adapter = DeepSeekClient(
                DeepSeekConfig(api_key="test-secret", base_url="https://deepseek.test"),
                client=client,
            )
            return await adapter.generate(
                agent="Support Agent",
                message="hello",
                forbidden_marker="LANGPROTECT-DEMO-CANDIDATE",
            )

    result = asyncio.run(run())
    assert "LANGPROTECT-DEMO-CANDIDATE" not in result
    assert "reserved marker removed" in result


def test_deepseek_client_maps_provider_failure_to_safe_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(401, json={"error": {"message": "do not expose me"}})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            adapter = DeepSeekClient(
                DeepSeekConfig(api_key="bad-key", base_url="https://deepseek.test"),
                client=client,
            )
            await adapter.generate(
                agent="Support Agent",
                message="hello",
                forbidden_marker="LANGPROTECT-DEMO-CANDIDATE",
            )

    try:
        asyncio.run(run())
    except DeepSeekError as exc:
        assert str(exc) == "DeepSeek could not produce a safe demo response."
    else:
        raise AssertionError("DeepSeekError was not raised")
