"""initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260502_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_data",
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("ticker"),
    )
    op.create_table(
        "signals",
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("ticker"),
    )
    op.create_table(
        "recommendations",
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("ticker"),
    )
    op.create_table(
        "recommendation_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recommendation_history_ticker",
        "recommendation_history",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        "ix_recommendation_history_timestamp",
        "recommendation_history",
        ["timestamp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_recommendation_history_timestamp", table_name="recommendation_history")
    op.drop_index("ix_recommendation_history_ticker", table_name="recommendation_history")
    op.drop_table("recommendation_history")
    op.drop_table("recommendations")
    op.drop_table("signals")
    op.drop_table("market_data")
