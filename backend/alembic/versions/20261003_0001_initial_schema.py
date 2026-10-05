"""Create initial DocuMind AI schema.

Revision ID: 20261003_0001
Revises:
Create Date: 2026-10-03 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261003_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("clerk_user_id", sa.String(255), nullable=False), sa.Column("email", sa.String(320), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.PrimaryKeyConstraint("id", name=op.f("pk_users")), sa.UniqueConstraint("clerk_user_id", name=op.f("uq_users_clerk_user_id")), sa.UniqueConstraint("email", name=op.f("uq_users_email")))
    op.create_index(op.f("ix_users_clerk_user_id"), "users", ["clerk_user_id"])
    op.create_index(op.f("ix_users_email"), "users", ["email"])
    op.create_table("documents", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("original_filename", sa.String(512), nullable=False), sa.Column("storage_key", sa.String(1024), nullable=False), sa.Column("mime_type", sa.String(127), nullable=False), sa.Column("size_bytes", sa.BigInteger(), nullable=False), sa.Column("page_count", sa.Integer(), nullable=True), sa.Column("processing_status", sa.String(32), nullable=False), sa.Column("processing_error", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_documents_user_id_users"), ondelete="CASCADE"), sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")), sa.UniqueConstraint("storage_key", name=op.f("uq_documents_storage_key")))
    op.create_index(op.f("ix_documents_user_id"), "documents", ["user_id"])
    op.create_table("conversations", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_conversations_user_id_users"), ondelete="CASCADE"), sa.PrimaryKeyConstraint("id", name=op.f("pk_conversations")))
    op.create_index(op.f("ix_conversations_user_id"), "conversations", ["user_id"])
    op.create_table("messages", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("role", sa.String(16), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("citations", sa.JSON(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], name=op.f("fk_messages_conversation_id_conversations"), ondelete="CASCADE"), sa.PrimaryKeyConstraint("id", name=op.f("pk_messages")))
    op.create_index(op.f("ix_messages_conversation_id"), "messages", ["conversation_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_messages_conversation_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_conversations_user_id"), table_name="conversations")
    op.drop_table("conversations")
    op.drop_index(op.f("ix_documents_user_id"), table_name="documents")
    op.drop_table("documents")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_clerk_user_id"), table_name="users")
    op.drop_table("users")
