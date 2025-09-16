from __future__ import annotations

from app.clients import GeminiClient
from app.core.models import (
    db_helper,
    Review,
    Response
)

class GenerateRepliesService:
    '''
    Use-case: for all Review(status='new') create Response(status='draft').
    ACID: one transaction per batch (session_scope).
    '''

    def __init__(
            self,
            model_name: str = 'gemini-1.5-flash',
            gemini: GeminiClient | None = None,
    ) -> None:
        self.model_name = model_name
        self.gem = gemini or GeminiClient(model_name=model_name)

    @staticmethod
    def _build_prompt(
            text: str | None,
            rating: int | None,
    ) -> str:
        base = 'Ты — поддержка бренда. Пиши очень кратко (2–4 предложения), дружелюбно, без спама.'
        base += f'Покупатель оценил товар: {rating or 0}/5. '
        if (text or '').strip():
            base += f'Отзыв: "{(text or "").strip()}". '
        else:
            base += 'Покупатель оставил только оценку без текста.'

        if rating is None or rating == 3:
            style = 'Нейтрально поблагодари и предложи помощь/уточнение.'
        elif rating >= 5:
            style = 'Тепло поблагодари и пригласи вернуться.'
        elif rating == 4:
            style = 'Поблагодари и мягко спроси, что можно улучшить.'
        elif rating == 2:
            style = 'Извинись, предложи помощь/обмен/возврат, попроси уточнить детали.'
        else:
            style = 'Искренне извинись, предложи оперативную помощь/возврат и способ связи.'
        return base + style

    def execute(self) -> int:
        crated = 0
        with db_helper.session_scope() as session:
            reviews = (
                session.query(Review)
                .filter(Review.status == 'new')
                .all()
            )

            for r in reviews:
                existing = (
                    session.query(Response.id)
                    .filter(Response.review_id == r.id)
                    .first()
                )
                if existing:
                    continue

                prompt = self._build_prompt(
                    r.text,
                    r.rating,
                )
                reply_text = self.gem.generate(prompt)

                session.add(
                    Response(
                        review_id=r.id,
                        reply_text=reply_text,
                        model=self.model_name,
                        status='draft',
                    )
                )
                r.status = 'answered'
                crated += 1

        return crated