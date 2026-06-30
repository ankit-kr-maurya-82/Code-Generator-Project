import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Select Model
model = genai.GenerativeModel("gemini-2.5-flash")


class AIServiceError(Exception):
    """Custom exception for AI errors."""
    pass


async def generate_code(prompt: str) -> str:
    """
    Generate code using Gemini AI.
    """

    if not prompt.strip():
        raise AIServiceError("Prompt cannot be empty.")

    system_prompt = f"""
You are an expert AI Code Generator.

Your job is to:
1. Generate clean, runnable code.
2. Explain the code.
3. Mention required libraries.
4. Suggest optimizations.
5. Find possible errors.

User Request:
{prompt}
"""

    try:
        response = model.generate_content(system_prompt)

        if response and hasattr(response, "text"):
            return response.text

        raise AIServiceError("No response received from Gemini.")

    except Exception as e:
        raise AIServiceError(f"Gemini Error: {str(e)}")