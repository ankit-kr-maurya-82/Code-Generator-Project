import os
from pathlib import Path

import httpx


class AIServiceError(Exception):
    """Raised when the AI provider cannot complete the request."""


class AIConfigurationError(AIServiceError):
    """Raised when required AI provider settings are missing."""


def _load_env_file() -> None:
    env_path = Path(".env")

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


_load_env_file()


async def generate_code(prompt: str) -> str:
    _load_env_file()

    provider = os.getenv("AI_PROVIDER", "openai").strip().lower()

    if provider == "gemini":
        return await _generate_with_gemini(prompt)

    if provider in {"openai", "groq"}:
        return await _generate_with_openai_compatible(prompt)

    raise AIConfigurationError(
        "AI_PROVIDER must be one of: openai, groq, gemini."
    )


async def _generate_with_openai_compatible(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    if not api_key:
        raise AIConfigurationError("OPENAI_API_KEY is missing. Add it to your .env file.")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert code generator. Return clear, runnable code "
                    "with a short explanation only when it helps."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        detail = error.response.text
        raise AIServiceError(f"AI provider returned an error: {detail}") from error
    except httpx.HTTPError as error:
        raise AIServiceError(f"Could not connect to the AI provider: {error}") from error

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise AIServiceError("AI provider returned an unexpected response.") from error


async def _generate_with_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    base_url = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
    )

    if not api_key:
        raise AIConfigurationError("GEMINI_API_KEY is missing. Add it to your .env file.")

    payload = {
        "model": model,
        "input": (
            "You are an expert code generator. Return clear, runnable code "
            "with a short explanation only when it helps.\n\n"
            f"User request:\n{prompt}"
        ),
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/interactions",
                headers={
                    "x-goog-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        detail = error.response.text
        raise AIServiceError(f"Gemini returned an error: {detail}") from error
    except httpx.HTTPError as error:
        raise AIServiceError(f"Could not connect to Gemini: {error}") from error

    data = response.json()

    try:
        return data["output_text"].strip()
    except (KeyError, TypeError) as error:
        raise AIServiceError("Gemini returned an unexpected response.") from error
