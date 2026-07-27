import httpx
import json
import logging
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

logger = logging.getLogger("verdict_chain")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def call_openrouter_json(prompt: str, model: str = None, max_tokens: int = 500) -> dict:
    """Call OpenRouter API with JSON response format enforced."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in backend/.env")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Verdict Chain",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model or OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a precise JSON-only API assistant. Output ONLY valid JSON matching the requested structure, with no markdown codeblocks or extra text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "max_tokens": max_tokens
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"OpenRouter API Error {response.status_code}: {response.text}")
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Clean potential markdown wrapping if present
        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]

        return json.loads(cleaned_content.strip())
