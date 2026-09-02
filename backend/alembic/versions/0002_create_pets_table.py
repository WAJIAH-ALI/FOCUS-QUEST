"""create pets table

Revision ID: 0002_create_pets
Revises: 0001_create_users
Create Date: 2026-09-02 00:05:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_create_pets"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None

growth_stage_enum = sa.Enum("egg", "hatchling", "juvenile", "adult", name="growth_stage")
pet_mood_enum = sa.Enum("happy", "neutral", "sad", "hungry", name="pet_mood")


def upgrade() -> None:
    bind = op.get_bind()
    growth_stage_enum.create(bind, checkfirst=True)
    pet_mood_enum.create(bind, checkfirst=True)

    op.create_table(
        "pets",
        sa.Column(
            "pet_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pet_name", sa.String(length=50), nullable=False),
        sa.Column("growth_stage", growth_stage_enum, nullable=False, server_default="egg"),
        sa.Column("food_type", sa.String(length=50), nullable=True),
        sa.Column("pet_age", sa.Integer(), nullable=True),
        sa.Column("pet_mood", pet_mood_enum, nullable=False, server_default="neutral"),
        sa.Column("current_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_pets_user_id_users", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_pets_user_id", "pets", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_pets_user_id", table_name="pets")
    op.drop_table("pets")
    pet_mood_enum.drop(op.get_bind(), checkfirst=True)
    growth_stage_enum.drop(op.get_bind(), checkfirst=True)