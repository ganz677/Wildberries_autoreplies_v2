from __future__ import annotations

import datetime

from sqlalchemy import select

from app.clients import WBClient
from app.core.logger import logger
from app.core.models import (
    Review,
    db_helper,
)


class FetchNewReviewsService:
    """
    - Use-case: take UNanswered reviews from WB by window and save to DB.
    - ACID: one transaction for the whole batch (session_scope) — all or nothing.
    - Idempotency: check duplicates by wb_id.
    """

    def __init__(self, wb_client: WBClient | None = None) -> None:
        self.wb_client = wb_client or WBClient.create()

    @staticmethod
    def _to_unix(dt: datetime.datetime) -> int:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.UTC)
        return int(dt.timestamp())

    @staticmethod
    def _parse_wb_iso(s: str | None) -> datetime.datetime:
        # WB: "2024-09-26T10:20:48+03:00"
        if not s:
            return datetime.datetime.now(datetime.UTC)
        return datetime.datetime.fromisoformat(s).astimezone(datetime.UTC)

    def execute(
        self,
        *,
        window_days: int = 3,
        page_size: int = 1000,
        max_total: int = 10000,
        order: str = 'dateDesc',
        nm_id: int | None = None,
    ) -> int:
        now = datetime.datetime.now(datetime.UTC)
        date_from = self._to_unix(now - datetime.timedelta(days=window_days))
        date_to = self._to_unix(now)

        logger.info(
            'Fetching WB reviews: window=%sdays, from=%s to=%s, page_size=%s, max_total=%s',
            window_days,
            datetime.datetime.fromtimestamp(date_from, tz=datetime.UTC),
            datetime.datetime.fromtimestamp(date_to, tz=datetime.UTC),
            page_size,
            max_total,
        )

        created = 0
        with db_helper.session_scope() as session:
            for item in self.wb_client.list_feedbacks(
                is_answered=False,
                date_from=date_from,
                date_to=date_to,
                order=order,
                page_size=page_size,
                max_total=max_total,
                nm_id=nm_id,
            ):
                wb_id = str(item.get('id') or '').strip()
                if not wb_id:
                    logger.warning('Skipping feedback without id: %s', item)
                    continue

                exists = session.execute(
                    select(Review.id).where(Review.wb_id == wb_id)
                ).scalar_one_or_none()
                if exists:
                    logger.debug('Feedback %s already exists, skipping', wb_id)
                    continue

                # sku -> productDetails.nmId
                pd = item.get('productDetails') or {}
                nm = pd.get('nmId')
                sku = str(nm) if nm is not None else None

                review = Review(
                    wb_id=wb_id,
                    user_name=item.get('userName'),
                    text=item.get('text'),
                    rating=item.get('productValuation'),
                    sku=sku,
                    created_at=self._parse_wb_iso(item.get('createdDate')),
                    status='new',
                )
                session.add(review)
                created += 1
                logger.info('Inserted new review wb_id=%s, rating=%s', wb_id, review.rating)

        logger.info('Total inserted reviews: %s', created)
        return created
