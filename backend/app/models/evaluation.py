from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    benchmark_id: Mapped[int] = mapped_column(
        ForeignKey("benchmarks.id"),
        nullable=False,
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    ground_truth: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
