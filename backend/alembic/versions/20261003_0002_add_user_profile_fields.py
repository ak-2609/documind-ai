"""Add Clerk-synchronized profile fields to users.

Revision ID: 20261003_0002
Revises: 20261003_0001
Create Date: 2026-10-03 00:00:01
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261003_0002"
down_revision: Union[str, Sequence[str], None] = "20261003_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("image_url", sa.String(length=2048), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "image_url")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
