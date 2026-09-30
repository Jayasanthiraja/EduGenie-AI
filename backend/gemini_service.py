import json

from google import genai
from google.genai import types

from .config import get_settings
from .schemas import QuizQuestion


class GeminiService:

    def __init__(self):
        self.settings = get_settings()
        self.client = None

        if self.settings.gemini_api_key:
            self.client = genai.Client(
                api_key=self.settings.gemini_api_key
            )

    def _require_client(self):
        if self.client is None:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add your Gemini API key to the .env file."
            )

        return self.client

    def generate(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None
    ) -> str:

        client = self._require_client()

        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048,
            system_instruction=system_instruction,
        )

        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=config,
        )

        text = getattr(response, "text", None)

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()

    def generate_quiz(
        self,
        passage: str,
        count: int
    ) -> list[QuizQuestion]:

        client = self._require_client()

        count = max(
            1,
            min(
                count,
                self.settings.max_quiz_questions
            )
        )

        prompt = f"""
Create exactly {count} multiple-choice questions
from the passage below.

Each question must test information contained
in the passage.

Each question must have exactly four different options.

The answer must exactly match one option.

Return JSON only.

PASSAGE:

{passage}
"""

        config = types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=3000,
            response_mime_type="application/json",
            response_schema=list[QuizQuestion],
        )

        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=config,
        )

        raw = getattr(response, "text", None)

        if not raw:
            raise RuntimeError(
                "Gemini returned an empty quiz response."
            )

        try:
            data = json.loads(raw)

            return [
                QuizQuestion.model_validate(item)
                for item in data
            ]

        except Exception as exc:
            raise RuntimeError(
                f"Could not parse Gemini quiz JSON: {exc}"
            ) from exc


_gemini = GeminiService()


def get_gemini_service() -> GeminiService:
    return _gemini