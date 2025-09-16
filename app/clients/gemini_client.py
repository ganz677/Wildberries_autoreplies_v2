from __future__ import annotations

from google import genai
from app.core.config import settings
from app.core.logger import logger


class GeminiClient:
    """
    Wrapper over the official Google SDK (google-genai).
    Pulls the key from settings.api_keys.gemini_token.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-1.5-flash",
    ) -> None:
        self.api_key = api_key or settings.api_keys.gemini_token
        if not self.api_key:
            raise RuntimeError("Gemini token is missing (settings.api_keys.gemini_token)")
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)

        logger.info("GeminiClient initialized with model=%s", self.model_name)

    def generate(self, prompt: str) -> str:
        """
        Send a text request to Gemini and return the response as a string.
        """
        logger.debug("Sending prompt to Gemini: %s", prompt[:200])

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
        except Exception as e:
            logger.error("Gemini API request failed: %s", e)
            raise

        try:
            if hasattr(response, "text") and response.text:
                text = response.text.strip()
            elif hasattr(response, "candidates"):
                text = response.candidates[0].content.parts[0].text.strip()
            else:
                raise RuntimeError("Unexpected Gemini response format")

            logger.debug("Gemini generated reply: %s", text[:200])
            return text

        except Exception as e:
            logger.error("Failed to parse Gemini response: %s", response)
            raise RuntimeError(f"Unexpected Gemini response {response}") from e
