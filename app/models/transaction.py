import datetime as dt
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base
from app.models.enums import TransactionType

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import User


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    type: Mapped[TransactionType] = mapped_column(
        Enum(
            TransactionType, name="transaction_type", create_constraint=True
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_date: Mapped[dt.date] = mapped_column(
        Date, nullable=False, index=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship(back_populates="transactions")
