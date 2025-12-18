import ollama
from app.config import OLLAMA_MODEL, OLLAMA_BASE_URL, TEMPERATURE


class _OllamaWrapper:
    def __init__(self, model: str, base_url: str | None = None, temperature: float | None = None):
        self.model = model
        self.temperature = temperature
        # create a client bound to the configured base URL (if provided)
        self.client = ollama.Client(host=base_url) if base_url else ollama.Client()

    def invoke(self, prompt: str):
        # Accept either a raw prompt string or a pre-built list of message dicts
        if isinstance(prompt, (list, tuple)):
            messages = list(prompt)
        else:
            messages = [{"role": "user", "content": prompt}]

        # Use the `chat` API and wrap the response to match expected interface
        resp = self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature} if self.temperature is not None else None,
        )

        class _Resp:
            def __init__(self, content: str):
                self.content = content

        return _Resp(resp.message.content if getattr(resp, 'message', None) else getattr(resp, 'response', ''))


def get_llm():
    return _OllamaWrapper(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=TEMPERATURE)
