import datetime
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.clients.gemini_client import GeminiClient
from app.clients.wb_client import WBClient
from app.core.models.base import Base
from app.core.models.db_helper import DataBaseHelper


@pytest.fixture(scope='function')
def db():
    """In-memory SQLite для каждого теста"""
    url = 'sqlite+pysqlite:///:memory:'
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    helper = DataBaseHelper(url, pool_pre_ping=False)
    helper.engine = engine
    helper.session_factory = SessionLocal

    import app.services.fetcher as s_fetcher
    import app.services.publisher as s_publisher
    import app.services.replier as s_replier

    s_fetcher.db_helper = helper
    s_replier.db_helper = helper
    s_publisher.db_helper = helper

    yield helper

    engine.dispose()


class FakeWBClient(WBClient):
    def __init__(self):
        self.replies = []

    def list_feedbacks(self, **_: Any):
        now = datetime.datetime.now(datetime.UTC).isoformat()
        yield {
            'id': 'WB1',
            'text': 'Спасибо, всё подошло',
            'productValuation': 5,
            'createdDate': now,
            'userName': 'Тест',
            'productDetails': {'nmId': 111},
        }

    def reply_to_feedback(self, feedback_id: str | int, text: str):
        self.replies.append((feedback_id, text))


class FakeGeminiClient(GeminiClient):
    def __init__(self, model='fake-model'):
        pass

    def generate(self, _: str) -> str:
        return 'Тестовый ответ'


@pytest.fixture
def fake_wb():
    return FakeWBClient()


@pytest.fixture
def fake_gemini():
    return FakeGeminiClient()
