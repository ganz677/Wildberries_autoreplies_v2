from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


class DataBaseHelper:
    def __init__(
        self,
        url: str,
        pool_pre_ping: bool,
    ):
        self.engine: Engine = create_engine(
            url=url,
            pool_pre_ping=pool_pre_ping,
        )
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        with self.session_factory() as session:
            yield session

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        with self.get_session() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def dispose(self):
        self.engine.dispose()


db_helper = DataBaseHelper(
    url=settings.db.url,
    pool_pre_ping=settings.db.pool_pre_ping,
)
