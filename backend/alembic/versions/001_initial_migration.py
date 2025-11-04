"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-01-04 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

NOVEL_STATUS_ENUM_NAME = "novelstatus"
STATUS_VALUES = ("DRAFT", "IN_PROGRESS", "COMPLETED", "PUBLISHED")


def _create_enum_if_needed(bind) -> sa.Enum:
    status_enum = sa.Enum(*STATUS_VALUES, name=NOVEL_STATUS_ENUM_NAME)
    status_enum.create(bind, checkfirst=True)
    return status_enum


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # For SQLite, we use String instead of Enum to avoid compatibility issues
    is_sqlite = bind.dialect.name == "sqlite"
    
    if is_sqlite:
        status_type = sa.String(length=20)
    else:
        status_enum = _create_enum_if_needed(bind)
        status_type = status_enum

    if "novels" not in inspector.get_table_names():
        op.create_table(
            "novels",
            sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("author", sa.String(length=100), nullable=True),
            sa.Column("genre", sa.String(length=50), nullable=True),
            sa.Column("synopsis", sa.Text(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", status_type, nullable=False, server_default="DRAFT"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        # Create indexes for better performance
        op.create_index("ix_novels_title", "novels", ["title"])
        op.create_index("ix_novels_author", "novels", ["author"])
        op.create_index("ix_novels_genre", "novels", ["genre"])
        op.create_index("ix_novels_status", "novels", ["status"])
        op.create_index("ix_novels_created_at", "novels", ["created_at"])
    else:
        columns = {column["name"] for column in inspector.get_columns("novels")}
        if "status" not in columns:
            op.add_column(
                "novels",
                sa.Column("status", status_type, nullable=False, server_default="DRAFT"),
            )
        if "description" not in columns:
            op.add_column("novels", sa.Column("description", sa.Text(), nullable=True))
        if "synopsis" not in columns:
            op.add_column("novels", sa.Column("synopsis", sa.Text(), nullable=True))

    if "world_settings" not in inspector.get_table_names():
        op.create_table(
            "world_settings",
            sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
            sa.Column("novel_id", sa.String(length=36), nullable=False),
            sa.Column("era", sa.String(length=100), nullable=True),
            sa.Column("locations", sa.JSON(), nullable=True),
            sa.Column("rules", sa.JSON(), nullable=True),
            sa.Column("culture", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("novel_id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "world_settings" in inspector.get_table_names():
        op.drop_table("world_settings")

    if "novels" in inspector.get_table_names():
        op.drop_table("novels")
    
    # Clean up enum if using PostgreSQL
    if bind.dialect.name != "sqlite":
        status_enum = sa.Enum(*STATUS_VALUES, name=NOVEL_STATUS_ENUM_NAME)
        status_enum.drop(bind, checkfirst=True)
