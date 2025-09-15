import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import Base

if TYPE_CHECKING:
    from .review import Review


class Response(Base):
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    review_id: Mapped[int] = mapped_column(
        ForeignKey('reviews.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )
    reply_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc='финальный текст ответа на отзыв'
    )
    model: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default='gemini-1.5-flash',
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default='draft', # draft->published->failed
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    published_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    review: Mapped['Review'] = relationship(
        back_populates='response',
    )