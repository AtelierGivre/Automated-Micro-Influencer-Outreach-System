"""Integration tests for the optional LangChain personalization backend.

These are skipped unless the packages from ``requirements-langchain.txt`` are
installed::

    pip install -r requirements.txt pytest
    pip install -r requirements-langchain.txt
    pytest -q

They use the real LangChain imports and construct real chat-model objects, but
stub ``invoke`` so the tests need no network and no API key.
"""

from __future__ import annotations

import pytest

import config
from src import personalize

langchain_core = pytest.importorskip("langchain_core")
langchain_anthropic = pytest.importorskip("langchain_anthropic")
langchain_openai = pytest.importorskip("langchain_openai")

from langchain_core.messages import (  # noqa: E402
    AIMessage,
    HumanMessage,
    SystemMessage,
)


def _select(monkeypatch, *, anthropic: bool) -> None:
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key" if anthropic else "")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "" if anthropic else "test-key")
    monkeypatch.setattr(config, "PERSONALIZE_BACKEND", "langchain")


def test_real_chat_model_objects_construct():
    from langchain_anthropic import ChatAnthropic
    from langchain_openai import ChatOpenAI

    anthropic_model = ChatAnthropic(
        model=config.ANTHROPIC_MODEL, api_key="test-key", max_tokens=400
    )
    openai_model = ChatOpenAI(
        model=config.OPENAI_MODEL, api_key="test-key", max_tokens=400
    )

    assert anthropic_model.model == config.ANTHROPIC_MODEL
    assert openai_model.model_name == config.OPENAI_MODEL


def test_anthropic_adapter_sends_real_message_types(monkeypatch):
    captured: dict = {}

    class FakeChatAnthropic:
        def __init__(self, **kwargs):
            captured["kwargs"] = kwargs

        def invoke(self, messages):
            captured["messages"] = messages
            return AIMessage(content="Anthropic adapter reply")

    monkeypatch.setattr(langchain_anthropic, "ChatAnthropic", FakeChatAnthropic)
    _select(monkeypatch, anthropic=True)

    assert personalize._langchain_available() is True
    assert personalize._use_langchain() is True
    assert personalize.llm_mode() == "LLM via LangChain"

    text = personalize._call_langchain("user prompt", "system prompt")

    assert text == "Anthropic adapter reply"
    assert isinstance(captured["messages"][0], SystemMessage)
    assert isinstance(captured["messages"][1], HumanMessage)
    assert captured["messages"][0].content == "system prompt"
    assert captured["messages"][1].content == "user prompt"
    assert captured["kwargs"]["max_tokens"] == 400


def test_openai_adapter_sends_real_message_types(monkeypatch):
    captured: dict = {}

    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            captured["kwargs"] = kwargs

        def invoke(self, messages):
            captured["messages"] = messages
            return AIMessage(content="OpenAI adapter reply")

    monkeypatch.setattr(langchain_openai, "ChatOpenAI", FakeChatOpenAI)
    _select(monkeypatch, anthropic=False)

    text = personalize._call_langchain("user prompt", "system prompt")

    assert text == "OpenAI adapter reply"
    assert isinstance(captured["messages"][0], SystemMessage)
    assert isinstance(captured["messages"][1], HumanMessage)
    assert captured["kwargs"]["max_tokens"] == 400


def test_adapter_joins_content_blocks(monkeypatch):
    class FakeChatAnthropic:
        def __init__(self, **kwargs):
            pass

        def invoke(self, messages):
            return AIMessage(
                content=[{"type": "text", "text": "block one "}, {"text": "block two"}]
            )

    monkeypatch.setattr(langchain_anthropic, "ChatAnthropic", FakeChatAnthropic)
    _select(monkeypatch, anthropic=True)

    assert personalize._call_langchain("p", "s") == "block one block two"


def test_direct_backend_ignores_installed_langchain(monkeypatch):
    _select(monkeypatch, anthropic=True)
    monkeypatch.setattr(config, "PERSONALIZE_BACKEND", "direct")

    assert personalize._use_langchain() is False
    assert personalize.llm_mode() == "LLM"
