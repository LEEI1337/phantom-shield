"""Tests for tool sandbox isolation."""

from nss.agent.tool_isolation import ToolSandbox


def _sample_search(**kwargs) -> str:
    return f"Results for: {kwargs.get('query', '')}"


def _slow_tool(**kwargs) -> str:
    import time
    time.sleep(10)
    return "done"


def test_execute_allowed_tool() -> None:
    sandbox = ToolSandbox()
    sandbox.register_tool("search", _sample_search)
    result = sandbox.execute_tool("search", {"query": "test"}, "user-1")
    assert result.vigil_verdict == "ALLOW"
    assert "Results for: test" in result.output
    assert result.execution_time_ms > 0


def test_vigil_deny_blocks_execution() -> None:
    sandbox = ToolSandbox()
    sandbox.register_tool("dangerous_tool", _sample_search)
    result = sandbox.execute_tool("dangerous_tool", {}, "user-1")
    assert result.vigil_verdict == "DENY"
    assert result.output == ""


def test_unregistered_tool() -> None:
    sandbox = ToolSandbox()
    result = sandbox.execute_tool("search", {"query": "test"}, "user-1")
    assert "not registered" in result.sandbox_metadata.get("error", "")


def test_timeout_enforcement() -> None:
    sandbox = ToolSandbox(default_timeout=0.5)
    sandbox.register_tool("search", _slow_tool)
    result = sandbox.execute_tool("search", {}, "user-1")
    assert "timed out" in result.sandbox_metadata.get("error", "").lower() or result.output == ""


def test_sandbox_metadata() -> None:
    sandbox = ToolSandbox()
    sandbox.register_tool("search", _sample_search)
    result = sandbox.execute_tool("search", {"query": "x"}, "user-1")
    assert result.sandbox_metadata.get("tool") == "search"
    assert result.sandbox_metadata.get("isolated") is True


def test_suspicious_args_blocked() -> None:
    sandbox = ToolSandbox()
    sandbox.register_tool("search", _sample_search)
    result = sandbox.execute_tool("search", {"query": "test; rm -rf /"}, "user-1")
    assert result.vigil_verdict == "DENY"
