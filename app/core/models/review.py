import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import Base

if TYPE_CHECKING:
    from .response import Response

class Review(Base):
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    wb_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True
    )
    user_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )
    text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    sku: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc='артикул wb'
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    pulled_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default='new',
        index=True
    )
    response: Mapped[Optional['Response']] = relationship(
        back_populates='review',
        uselist=False,
        cascade='all, delete-orphan',
    )