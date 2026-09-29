"""create focus, diary, memory, and map progression tables

Revision ID: 0004_create_focus_diary_memory
Revises: 0003_create_quests
Create Date: 2026-09-29 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "0004_create_focus_diary_memory"
down_revision = "0003_create_quests"
branch_labels = None
depends_on = None

focus_session_status_enum = postgresql.ENUM("started", "paused", "completed", "cancelled", name="focus_session_status", create_type=False)
distraction_action_enum = postgresql.ENUM("parked", "converted_to_quest", "dismissed", name="distraction_action", create_type=False)
memory_source_type_enum = postgresql.ENUM("diary", "focus_habit", "coping_strategy", "preference", name="memory_source_type", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create enums
    focus_session_status_enum.create(bind, checkfirst=True)
    distraction_action_enum.create(bind, checkfirst=True)
    memory_source_type_enum.create(bind, checkfirst=True)

    # 1. Extend quests table for subtasks and ADHD micro-task breakdown
    op.add_column("quests", sa.Column("parent_quest_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("quests", sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True))
    op.add_column("quests", sa.Column("tags", sa.JSON(), nullable=True))
    op.add_column("quests", sa.Column("is_micro_task", sa.Boolean(), nullable=False, server_default="false"))
    op.create_foreign_key(
        "fk_quests_parent_quest_id_quests",
        "quests",
        "quests",
        ["parent_quest_id"],
        ["quest_id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_quests_parent_quest_id", "quests", ["parent_quest_id"])

    # 2. Create focus_sessions table
    op.create_table(
        "focus_sessions",
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quest_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="25"),
        sa.Column("actual_duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", focus_session_status_enum, nullable=False, server_default="started"),
        sa.Column("distraction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_focus_sessions_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["quest_id"], ["quests.quest_id"], name="fk_focus_sessions_quest_id_quests", ondelete="SET NULL"
        ),
    )
    op.create_index("ix_focus_sessions_user_id", "focus_sessions", ["user_id"])
    op.create_index("ix_focus_sessions_quest_id", "focus_sessions", ["quest_id"])
    op.create_index("ix_focus_sessions_status", "focus_sessions", ["status"])

    # 3. Create distraction_logs table ("Park a Thought")
    op.create_table(
        "distraction_logs",
        sa.Column(
            "log_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thought_content", sa.Text(), nullable=False),
        sa.Column("action_taken", distraction_action_enum, nullable=False, server_default="parked"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["focus_sessions.session_id"], name="fk_distraction_logs_session_id", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_distraction_logs_user_id", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_distraction_logs_session_id", "distraction_logs", ["session_id"])
    op.create_index("ix_distraction_logs_user_id", "distraction_logs", ["user_id"])

    # 4. Create diary_entries table
    op.create_table(
        "diary_entries",
        sa.Column(
            "entry_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("mood_tags", sa.JSON(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("ai_reflection", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_diary_entries_user_id_users", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_diary_entries_user_id", "diary_entries", ["user_id"])

    # 5. Create agent_memory table with pgvector column
    op.create_table(
        "agent_memory",
        sa.Column(
            "memory_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", memory_source_type_enum, nullable=False, server_default="diary"),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_agent_memory_user_id_users", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_agent_memory_user_id", "agent_memory", ["user_id"])
    op.create_index("ix_agent_memory_source_type", "agent_memory", ["source_type"])

    # Create HNSW index for high-speed cosine vector similarity search
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_agent_memory_embedding "
        "ON agent_memory USING hnsw (embedding vector_cosine_ops)"
    )

    # 6. Create map_nodes table
    op.create_table(
        "map_nodes",
        sa.Column("node_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("zone_id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("required_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rewards_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_map_nodes_zone_id", "map_nodes", ["zone_id"])

    # 7. Create user_map_progression table
    op.create_table(
        "user_map_progression",
        sa.Column(
            "progression_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("is_unlocked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_user_map_progression_user_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["node_id"], ["map_nodes.node_id"], name="fk_user_map_progression_node_id", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_user_map_progression_user_id", "user_map_progression", ["user_id"])
    op.create_index("ix_user_map_progression_node_id", "user_map_progression", ["node_id"])


def downgrade() -> None:
    bind = op.get_bind()

    # Drop user_map_progression & map_nodes
    op.drop_index("ix_user_map_progression_node_id", table_name="user_map_progression")
    op.drop_index("ix_user_map_progression_user_id", table_name="user_map_progression")
    op.drop_table("user_map_progression")
    op.drop_index("ix_map_nodes_zone_id", table_name="map_nodes")
    op.drop_table("map_nodes")

    # Drop agent_memory
    op.execute("DROP INDEX IF EXISTS ix_agent_memory_embedding")
    op.drop_index("ix_agent_memory_source_type", table_name="agent_memory")
    op.drop_index("ix_agent_memory_user_id", table_name="agent_memory")
    op.drop_table("agent_memory")

    # Drop diary_entries
    op.drop_index("ix_diary_entries_user_id", table_name="diary_entries")
    op.drop_table("diary_entries")

    # Drop distraction_logs
    op.drop_index("ix_distraction_logs_user_id", table_name="distraction_logs")
    op.drop_index("ix_distraction_logs_session_id", table_name="distraction_logs")
    op.drop_table("distraction_logs")

    # Drop focus_sessions
    op.drop_index("ix_focus_sessions_status", table_name="focus_sessions")
    op.drop_index("ix_focus_sessions_quest_id", table_name="focus_sessions")
    op.drop_index("ix_focus_sessions_user_id", table_name="focus_sessions")
    op.drop_table("focus_sessions")

    # Remove quests columns
    op.drop_index("ix_quests_parent_quest_id", table_name="quests")
    op.drop_constraint("fk_quests_parent_quest_id_quests", "quests", type_="foreignkey")
    op.drop_column("quests", "is_micro_task")
    op.drop_column("quests", "tags")
    op.drop_column("quests", "estimated_duration_minutes")
    op.drop_column("quests", "parent_quest_id")

    # Drop enums
    memory_source_type_enum.drop(bind, checkfirst=True)
    distraction_action_enum.drop(bind, checkfirst=True)
    focus_session_status_enum.drop(bind, checkfirst=True)
