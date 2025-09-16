from __future__ import annotations

from abc import (
    ABC,
    abstractmethod
)
from typing import (
    Iterator,
    Optional,
    Any,
    Mapping
)

import requests


class IApiClient(ABC):
    '''
    Abstract transport class for HTTP-requests
    '''
    @abstractmethod
    def get(
            self,
            url: str,
            *,
            headers: Mapping[str, str] | None =  None,
            params: Mapping[str, Any] | None = None,
            timeout: int = 30,
    ) -> dict:
        ...

    @abstractmethod
    def post(
            self,
            url: str,
            *,
            headers: Mapping[str, str] | None = None,
            json: Mapping[str, Any] | None = None,
            timeout: int = 30,
    ) -> dict | None:
        ...

class RequestsClient(IApiClient):
    '''
    Implementing transport via requests
    '''
    def get(
            self,
            url: str,
            *,
            headers=None,
            params=None,
            timeout: int = 30,
    ) -> dict:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def post(
            self,
            url: str,
            *,
            headers=None,
            json=None,
            timeout: int = 30,
    ) -> dict | None:
        response = requests.post(url, headers=headers, json=json, timeout=timeout)
        if response.status_code not in (200, 204):
            response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return None


class IReviewApi(ABC):
    '''
    Interface for working with WB reviews
    '''

    @abstractmethod
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
        ...

    @abstractmethod
    def reply_to_feedback(
            self,
            feedback_id: str | int,
            text: str,
    ) -> None:
        ...