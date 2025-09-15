from contextlib import contextmanager

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from core.config import settings



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
    def get_session(self) -> Session:
        with self.session_factory() as session:
            yield session

    @contextmanager
    def session_scope(self) -> Session:
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