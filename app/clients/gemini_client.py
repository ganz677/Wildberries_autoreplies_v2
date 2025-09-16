# app/clients/gemini_client.py
from __future__ import annotations

from typing import Any

from google import genai

from app.core.config import settings
from app.core.logger import logger


class GeminiClient:
    def __init__(self, api_key: str | None = None, model_name: str = 'gemini-1.5-flash') -> None:
        self.api_key = api_key or settings.api_keys.gemini_token
        if not self.api_key:
            raise RuntimeError('Gemini token is missing (settings.api_keys.gemini_token)')
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        logger.info('GeminiClient initialized with model=%s', self.model_name)

    def generate(self, prompt: str) -> str:
        logger.debug('Sending prompt to Gemini: %s', prompt[:200])
        try:
            response: Any = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            logger.error('Gemini API request failed: %s', e)
            raise

        text = getattr(response, 'text', None)
        if isinstance(text, str) and text.strip():
            out = text.strip()
            logger.debug('Gemini generated reply: %s', out[:200])
            return out

        logger.error('Unexpected Gemini response (no .text): %r', response)
        raise RuntimeError('Unexpected Gemini response: missing text')
