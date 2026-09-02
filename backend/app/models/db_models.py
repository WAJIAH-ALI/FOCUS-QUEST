import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    String,
    Integer,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GrowthStage(str, enum.Enum):
    egg = "egg"
    hatchling = "hatchling"
    juvenile = "juvenile"
    adult = "adult"


class PetMood(str, enum.Enum):
    happy = "happy"
    neutral = "neutral"
    sad = "sad"
    hungry = "hungry"


class QuestDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestStatus(str, enum.Enum):
    incomplete = "incomplete"
    done = "done"


class QuestPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_speed_per_click: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    pets: Mapped[list["Pet"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quests: Mapped[list["Quest"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.user_id} {self.username!r}>"


class Pet(Base):
    __tablename__ = "pets"

    pet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    pet_name: Mapped[str] = mapped_column(String(50), nullable=False)
    growth_stage: Mapped[GrowthStage] = mapped_column(
        SAEnum(GrowthStage, name="growth_stage"), nullable=False, default=GrowthStage.egg
    )
    food_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pet_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pet_mood: Mapped[PetMood] = mapped_column(
        SAEnum(PetMood, name="pet_mood"), nullable=False, default=PetMood.neutral
    )
    current_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="pets")

    def __repr__(self) -> str:
        return f"<Pet {self.pet_id} {self.pet_name!r} stage={self.growth_stage}>"


class Quest(Base):
    __tablename__ = "quests"

    quest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty_level: Mapped[QuestDifficulty] = mapped_column(
        SAEnum(QuestDifficulty, name="quest_difficulty"), nullable=False, default=QuestDifficulty.easy
    )
    xp_assigned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deadline_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # task deadline
    status: Mapped[QuestStatus] = mapped_column(
        SAEnum(QuestStatus, name="quest_status"), nullable=False, default=QuestStatus.incomplete
    )
    priority: Mapped[QuestPriority] = mapped_column(
        SAEnum(QuestPriority, name="quest_priority"), nullable=False, default=QuestPriority.medium
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="quests")

    def __repr__(self) -> str:
        return f"<Quest {self.quest_id} {self.title!r} status={self.status}>"