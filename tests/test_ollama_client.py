from unittest.mock import MagicMock

from src.llm.ollama_client import OllamaClient, TokenUsage


def _client_with_fake(response: dict) -> tuple[OllamaClient, MagicMock]:
    client = OllamaClient("http://localhost:11434", "m-default", "m-deep")
    fake = MagicMock()
    fake.chat.return_value = response
    client._client = fake
    return client, fake


def test_complete_maps_response():
    client, fake = _client_with_fake(
        {"message": {"content": "hello"}, "prompt_eval_count": 12, "eval_count": 7}
    )
    text, usage = client.complete([{"role": "user", "content": "hi"}], system="sys")
    assert text == "hello"
    assert isinstance(usage, TokenUsage)
    assert usage.input_tokens == 12
    assert usage.output_tokens == 7
    assert usage.model == "m-default"
    sent = fake.chat.call_args.kwargs["messages"]
    assert sent[0]["role"] == "system"
    assert sent[1]["content"] == "hi"


def test_complete_deep_uses_deep_model():
    client, _ = _client_with_fake(
        {"message": {"content": "x"}, "prompt_eval_count": 1, "eval_count": 1}
    )
    _, usage = client.complete([{"role": "user", "content": "hi"}], deep=True)
    assert usage.model == "m-deep"
