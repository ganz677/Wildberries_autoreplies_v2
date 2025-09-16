from __future__ import annotations

from google import genai

from core.config import settings

class GeminiClient:
    '''
    Wrapper over the official Google SDK (google-genai).
    Pulls the key from settings.api_keys.gemini_token.
    '''
    def __init__(
            self,
            api_key: str | None = None,
            model_name: str = 'gemini-1.5-flash',
    ) -> None:
        self.api_key = api_key or settings.api_keys.gemini_token
        if not self.api_key:
            raise RuntimeError('Gemini token is missing (settings.api_keys.gemini_token)')
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        '''
        Send a text request to Gemini and return the response as a string
        '''
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        try:
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f'Unexpected gemini response {response}:') from e