from __future__ import annotations

import datetime
import time
from collections.abc import Iterable

from sqlalchemy import select

from app.clients import WBClient
from app.core.logger import logger
from app.core.models import (
    Response,
    Review,
    db_helper,
)


class PublishRepliesService:
    """
    Use-case: publish responses to WB.
    ACID: one transaction for EVERY response (so that WB and DB do not diverge).
    Reliability: soft retry/backoff for temporary network/HTTP errors.
    """

    def __init__(
        self,
        wb_client: WBClient | None = None,
        *,
        max_retries: int = 3,
        backoff_sec: float = 0.8,  # -> 0.8 1.6 2.4 ...
    ) -> None:
        self.wb = wb_client or WBClient.create()
        self.max_retries = max_retries
        self.backoff_sec = backoff_sec

    def _iter_draft_ids(self, limit: int | None = None) -> Iterable[int]:
        """
        Quickly get a list of IDs of all drafts (Response.status == "draft") -
        without dragging entire objects and keeping a long transaction.
        """
        with db_helper.get_session() as session:
            query = select(Response.id).where(Response.status == 'draft')
            ids = (
                session.execute(query).scalars().fetchmany(limit)
                if limit
                else session.execute(query).scalars().all()
            )
            logger.debug('Found %d draft responses to publish', len(ids))
            return list(ids)

    def _publish_one(self, resp_id: int) -> bool:
        with db_helper.session_scope() as session:
            resp = session.get(Response, resp_id)
            if not resp or resp.status != 'draft':
                logger.warning('Response %s not found or not in draft state', resp_id)
                return False

            review = session.get(Review, resp.review_id)
            if not review:
                logger.error('Review for response %s not found', resp_id)
                return False

            logger.info(
                'Publishing reply (resp_id=%s, review_id=%s, wb_id=%s)',
                resp_id,
                review.id,
                review.wb_id,
            )

            self.wb.reply_to_feedback(review.wb_id, resp.reply_text)

            now = datetime.datetime.now(datetime.UTC)
            resp.status = 'published'
            resp.published_at = now
            review.status = 'published'

            logger.info('Successfully published reply %s for review %s', resp_id, review.wb_id)
            return True

    def execute(self, *, limit: int | None = None) -> int:
        published = 0
        draft_ids = self._iter_draft_ids(limit)

        if not draft_ids:
            logger.info('No draft responses found to publish')
            return 0

        for resp_id in draft_ids:
            attempt = 0
            while True:
                try:
                    ok = self._publish_one(resp_id)
                    if ok:
                        published += 1
                    break
                except Exception as e:
                    attempt += 1
                    logger.error(
                        'Error publishing response %s (attempt %d/%d): %s',
                        resp_id,
                        attempt,
                        self.max_retries,
                        e,
                    )
                    if attempt > self.max_retries:
                        logger.critical(
                            'Giving up on response %s after %d attempts', resp_id, attempt
                        )
                        break
                    backoff = self.backoff_sec * attempt
                    logger.warning('Retrying response %s after %.1fs...', resp_id, backoff)
                    time.sleep(backoff)

        logger.info('Total published responses: %d', published)
        return published
