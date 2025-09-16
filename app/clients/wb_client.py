from __future__ import annotations

import time

from typing import (
    Iterator,
    Optional,
    Dict,
    Any,
)

from app.core.config import settings
from .interfaces import (
    IApiClient,
    RequestsClient,
    IReviewApi
)

class WBClient(IReviewApi):
    '''
    - Depends on IApiClient abstraction (transport can be substituted).
    - WBClient.create() — convenient to collect from settings
    - Generator list_feedbacks page by page and carefully to rate limit WB (~3 rps, burst ~6)
    '''

    BASE_URL = 'https://feedbacks-api.wildberries.ru'

    def __init__(
            self,
            token: str,
            transport: IApiClient,
            timeout: int = 30,
    ) -> None:
        self.token = token
        self.transport = transport
        self.timeout = timeout

    @classmethod
    def create(cls) -> 'WBClient':
        token = settings.api_keys.wb_token
        if not token:
            raise RuntimeError('WB Token is missing (settings.api_keys.wb_token)')
        return cls(token=token, transport=RequestsClient())

    def _headers(self) -> dict[str, str]:
        return {
            'Authorization': self.token,
            'Content-Type': 'application/json',
        }

    def list_feedbacks(
            self,
            *,
            is_answered: bool,
            date_from: Optional[int] = None,
            date_to: Optional[int] = None,
            order: str = 'dateDesc',
            page_size: int = 1000,
            max_total: int = 10000,
            nm_id: Optional[int] = None,
            sleep_between_pages: float = 0.2,
    ) -> Iterator[dict]:
        '''
        GET /api/v1/feedbacks
        - Returns a generator of elements from data.feedbacks (dict).
        - Mandatory parameters for WB: isAnswered, take, skip (we generate them).
        - Supported: order, dateFrom, dateTo, nmId.
        :param is_answered:
        :param date_from:
        :param date_to:
        :param order:
        :param page_size:
        :param max_total:
        :param nm_id:
        :param sleep_between_pages:
        :return:
        '''
        if not (1 <= page_size <= 5000):
            raise ValueError('Page size must be between 1 and 5000.')


        skip = 0 # сколько отзывов пропустили
        taken = 0 # сколько получили


        while taken < max_total: # пока мы не набрали max_total продолжаем запросы
            take = min(page_size, max_total - taken) # размер текущей страницы если остаётся меньше, чем page_size, берется остаток

            params: Dict[str, Any] = {
                'isAnswered': str(is_answered).lower(),
                'take': take,
                'skip': skip,
                'order': order,
            }

            if date_from is not None:
                params['dateFrom'] = int(date_from)
            if date_to is not None:
                params['dateTo'] = int(date_to)
            if nm_id is not None:
                params['nmId'] = int(nm_id)

            url = f'{self.BASE_URL}/api/v1/feedbacks'
            payload = self.transport.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=self.timeout
            )
            items = (payload.get('data') or {}).get('feedbacks') or []

            if not items:
                break

            for item in items:
                yield item

            count = len(items)
            taken += count
            skip += count

            if sleep_between_pages:
                time.sleep(sleep_between_pages)


    def reply_to_feedback(
            self,
            feedback_id: str | int,
            text: str,
    ) -> None:
        """
        POST /api/v1/feedbacks/answer
        Body: {"id": "<feedback_id>", "text": "<answer_text>"}
        Success: 204 No Content (sometimes 200 OK).
        """
        url = f'{self.BASE_URL}/api/v1/feedbacks/answer'
        payload = {
            'id': str(feedback_id),
            'text': text,
        }
        self.transport.post(
            url=url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )