import os

import google.generativeai as genai
import httpx
from dotenv import load_dotenv

load_dotenv()


class AIServiceError(Exception):
    """Custom exception for AI errors."""

    pass


def get_system_prompt(prompt: str) -> str:
    return f"""
You are a beginner-friendly AI Code Generator.

Answer in simple English and keep the response easy to understand.

Use exactly these four section headings in this order:
Result
   - Give the direct answer first.
Code
   - Show the simplest runnable code example.
   - Use Python unless the user asks for another language.
   - Always wrap code in a fenced Markdown code block with the language name.
Explanation
   - Explain each important line in short, clear sentences.
Required Libraries
   - Say "No extra libraries needed" if none are needed.

Rules:
- If the request is simple, like "2+2", do not over-explain.
- Avoid advanced words when a simple word works.
- Keep examples short and practical.

User Request:
{prompt}
"""


def get_setting(name: str, fallback: str = "") -> str:
    return os.getenv(name, fallback).strip()


async def generate_with_chat_api(prompt: str, provider: str) -> str:
    model = get_setting("MODEL") or get_setting(f"{provider.upper()}_MODEL")
    base_url = get_setting("BASE_URL") or get_setting(f"{provider.upper()}_BASE_URL")
    api_key = get_setting(f"{provider.upper()}_API_KEY")

    if not model:
        raise AIServiceError("MODEL is missing in .env.")

    if not base_url:
        raise AIServiceError("BASE_URL is missing in .env.")

    if not api_key:
        raise AIServiceError(f"{provider.upper()}_API_KEY is missing in .env.")

    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": get_system_prompt(prompt),
            }
        ],
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if response.status_code >= 400:
        raise AIServiceError(f"{provider.title()} Error: {response.text}")

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise AIServiceError(f"No response received from {provider.title()}.") from error


async def generate_with_gemini(prompt: str) -> str:
    api_key = get_setting("GEMINI_API_KEY")
    model_name = get_setting("MODEL") or get_setting("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise AIServiceError("GEMINI_API_KEY is missing in .env.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(get_system_prompt(prompt))

    if response and hasattr(response, "text"):
        return response.text

    raise AIServiceError("No response received from Gemini.")


async def generate_code(prompt: str) -> str:
    """
    Generate code using the selected AI provider.
    """

    if not prompt.strip():
        raise AIServiceError("Prompt cannot be empty.")

    provider = get_setting("AI_PROVIDER", "groq").lower()

    try:
        if provider in {"groq", "openai"}:
            return await generate_with_chat_api(prompt, provider)

        if provider == "gemini":
            return await generate_with_gemini(prompt)

        raise AIServiceError("AI_PROVIDER must be groq, openai, or gemini.")
    except AIServiceError:
        raise
    except Exception as error:
        raise AIServiceError(f"{provider.title()} Error: {str(error)}") from error
