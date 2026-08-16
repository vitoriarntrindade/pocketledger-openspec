from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base
from app.models.enums import TransactionType

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.user import User


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "name", "type", name="uq_category_user_name_type"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        Enum(
            TransactionType, name="transaction_type", create_constraint=True
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="categories")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="category"
    )
