"""Thin LLM gateway: Gemini or Groq over REST, JSON-only output, demo fallback."""
import base64, json, os, re
from dataclasses import dataclass
import httpx

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_VISION = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_TEXT = os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile")


class LLMError(Exception):
    pass


@dataclass
class Creds:
    provider: str = "gemini"
    key: str = ""

    @classmethod
    def build(cls, provider: str | None, key: str | None) -> "Creds":
        provider = (provider or "gemini").lower()
        if provider not in ("gemini", "groq"):
            provider = "gemini"
        key = (key or "").strip() or os.getenv(f"{provider.upper()}_API_KEY", "")
        return cls(provider, key)

    @property
    def demo(self) -> bool:
        return not self.key


def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    raise LLMError("The model returned a response that was not valid JSON. Try again.")


def ask_json(prompt: str, creds: Creds, images: list[tuple[bytes, str]] | None = None) -> dict:
    images = images or []
    try:
        if creds.provider == "gemini":
            return _gemini(prompt, creds.key, images)
        return _groq(prompt, creds.key, images)
    except httpx.TimeoutException:
        raise LLMError("The AI provider timed out. Try a smaller file or retry.")
    except httpx.HTTPError as e:
        raise LLMError(f"Could not reach the AI provider: {e}")


def _raise_for(r: httpx.Response):
    if r.status_code in (400, 401, 403):
        raise LLMError(f"API key rejected or request invalid ({r.status_code}). Check your key and model name.")
    if r.status_code == 429:
        raise LLMError("Rate limit reached on your API key. Wait a minute and retry.")
    if r.status_code >= 400:
        raise LLMError(f"Provider error {r.status_code}: {r.text[:200]}")


def _gemini(prompt, key, images):
    parts = [{"text": prompt}] + [
        {"inline_data": {"mime_type": m, "data": base64.b64encode(b).decode()}} for b, m in images
    ]
    r = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json={"contents": [{"parts": parts}],
              "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}},
        timeout=90,
    )
    _raise_for(r)
    try:
        return parse_json(r.json()["candidates"][0]["content"]["parts"][0]["text"])
    except (KeyError, IndexError):
        raise LLMError("The model returned no content (it may have been blocked). Try another image.")


def _groq(prompt, key, images):
    content = [{"type": "text", "text": prompt}] + [
        {"type": "image_url", "image_url": {"url": f"data:{m};base64,{base64.b64encode(b).decode()}"}}
        for b, m in images
    ]
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": GROQ_VISION if images else GROQ_TEXT,
              "messages": [{"role": "user", "content": content if images else prompt}],
              "temperature": 0.3, "response_format": {"type": "json_object"}},
        timeout=90,
    )
    _raise_for(r)
    try:
        return parse_json(r.json()["choices"][0]["message"]["content"])
    except (KeyError, IndexError):
        raise LLMError("The model returned no content.")
