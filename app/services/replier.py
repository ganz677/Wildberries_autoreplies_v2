from __future__ import annotations

from app.core.logger import logger
from app.clients import GeminiClient
from app.core.models import (
    db_helper,
    Review,
    Response,
)


class GenerateRepliesService:
    """
    Use-case: for all Review(status='new') create Response(status='draft').
    ACID: one transaction per batch (session_scope).
    """

    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        gemini: GeminiClient | None = None,
    ) -> None:
        self.model_name = model_name
        self.gem = gemini or GeminiClient(model_name=model_name)

    @staticmethod
    def _build_prompt(text: str | None, rating: int | None) -> str:
        base = "Ты — поддержка бренда. Пиши очень кратко (2–4 предложения), дружелюбно, без спама."
        base += f" Покупатель оценил товар: {rating or 0}/5. "
        if (text or "").strip():
            base += f'Отзыв: "{(text or "").strip()}". '
        else:
            base += "Покупатель оставил только оценку без текста."

        if rating is None or rating == 3:
            style = "Нейтрально поблагодари и предложи помощь/уточнение."
        elif rating >= 5:
            style = "Тепло поблагодари и пригласи вернуться."
        elif rating == 4:
            style = "Поблагодари и мягко спроси, что можно улучшить."
        elif rating == 2:
            style = "Извинись, предложи помощь/обмен/возврат, попроси уточнить детали."
        else:
            style = "Искренне извинись, предложи оперативную помощь/возврат и способ связи."
        return base + style

    def execute(self) -> int:
        logger.info("Generating replies for new reviews...")
        created = 0
        with db_helper.session_scope() as session:
            reviews = (
                session.query(Review)
                .filter(Review.status == "new")
                .all()
            )
            logger.debug("Found %s reviews with status=new", len(reviews))

            for r in reviews:
                existing = (
                    session.query(Response.id)
                    .filter(Response.review_id == r.id)
                    .first()
                )
                if existing:
                    logger.debug("Review %s already has a response, skipping", r.wb_id)
                    continue

                logger.debug("Building prompt for review %s (rating=%s)", r.wb_id, r.rating)
                prompt = self._build_prompt(r.text, r.rating)

                try:
                    reply_text = self.gem.generate(prompt)
                except Exception as e:
                    logger.error("Gemini failed to generate reply for review %s: %s", r.wb_id, e)
                    continue

                session.add(
                    Response(
                        review_id=r.id,
                        reply_text=reply_text,
                        model=self.model_name,
                        status="draft",
                    )
                )
                r.status = "answered"
                created += 1
                logger.info("Generated reply for review %s", r.wb_id)

        logger.info("Total generated replies: %s", created)
        return created
