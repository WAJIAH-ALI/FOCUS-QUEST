"""create quests table

Revision ID: 0003_create_quests
Revises: 0002_create_pets
Create Date: 2026-09-02 00:10:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_create_quests"
down_revision = "0002_create_pets"
branch_labels = None
depends_on = None

difficulty_enum = sa.Enum("easy", "medium", "hard", "extreme", "extreme_final_boss", name="quest_difficulty")
status_enum = sa.Enum("incomplete", "done", name="quest_status")
priority_enum = sa.Enum("low", "medium", "high", "critical", "critical_final_boss", name="quest_priority")


def upgrade() -> None:
    bind = op.get_bind()
    difficulty_enum.create(bind, checkfirst=True)
    status_enum.create(bind, checkfirst=True)
    priority_enum.create(bind, checkfirst=True)

    op.create_table(
        "quests",
        sa.Column(
            "quest_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty_level", difficulty_enum, nullable=False, server_default="easy"),
        sa.Column("xp_assigned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deadline_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", status_enum, nullable=False, server_default="incomplete"),
        sa.Column("priority", priority_enum, nullable=False, server_default="medium"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_quests_user_id_users", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_quests_user_id", "quests", ["user_id"])
    op.create_index("ix_quests_status", "quests", ["status"])


def downgrade() -> None:
    op.drop_index("ix_quests_status", table_name="quests")
    op.drop_index("ix_quests_user_id", table_name="quests")
    op.drop_table("quests")
    priority_enum.drop(op.get_bind(), checkfirst=True)
    status_enum.drop(op.get_bind(), checkfirst=True)
    difficulty_enum.drop(op.get_bind(), checkfirst=True)