from __future__ import annotations

import datetime
import time

from typing import Iterable

from sqlalchemy import select

from app.clients import WBClient
from app.core.models import (
    db_helper,
    Review,
    Response
)


class PublishRepliesService:
    '''
    Use-case: publish responses to WB.
    ACID: one transaction for EVERY response (so that WB and DB do not diverge).
    Reliability: soft retry/backoff for temporary network/HTTP errors.
    '''

    def __init__(
            self,
            wb_client: WBClient | None = None,
            *,
            max_retries: int = 3,
            backoff_sec: float = 0.8, # -> 0.8 1.6 2.4 ...
    ) -> None:
        self.wb = wb_client or WBClient.create()
        self.max_retries = max_retries
        self.backoff_sec = backoff_sec

    def _iter_draft_ids(
            self,
            limit: int | None = None,
    ) -> Iterable[int]:
        '''
        Quickly get a list of IDs of all drafts (Response.status == "draft") -
        - without dragging entire objects and keeping a long transaction.
        :param limit:
        :return:
        '''
        with db_helper.get_session() as session:
            query = select(Response.id).where(Response.status == "draft")
            if limit:
                return [rid for rid in session.execute(query).scalars().fetchmany(limit)]
            return [rid for rid in session.execute(query).scalars().all()]

    def _publish_one(
            self,
            resp_id: int
    ) -> bool:
        with db_helper.session_scope() as session:
            resp = session.get(Response, resp_id)
            if not resp or resp.status != 'draft':
                return False

            review = session.get(Review, resp.review_id)
            if not review:
                return False

            self.wb.reply_to_feedback(
                review.wb_id,
                resp.reply_text
            )

            now = datetime.datetime.now(datetime.timezone.utc)
            resp.status = 'published'
            resp.published_at = now
            review.status = 'published'
            return True

    def execute(
            self,
            *,
            limit: int | None = None,
    ) -> int:
        published = 0
        for resp_id in self._iter_draft_ids(limit):
            attempt = 0
            while True:
                try:
                    ok = self._publish_one(resp_id)
                    if ok:
                        published += 1
                    break
                except Exception:
                    attempt += 1
                    if attempt > self.max_retries:
                        break
                    time.sleep(self.backoff_sec * attempt)
        return  published
