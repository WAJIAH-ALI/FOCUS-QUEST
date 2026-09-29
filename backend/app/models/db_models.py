import enum
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# ----------------- Enums -----------------

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
    extreme = "extreme"
    extreme_final_boss = "extreme_final_boss"


class QuestStatus(str, enum.Enum):
    incomplete = "incomplete"
    done = "done"


class QuestPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    critical_final_boss = "critical_final_boss"


class FocusSessionStatus(str, enum.Enum):
    started = "started"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"


class DistractionAction(str, enum.Enum):
    parked = "parked"
    converted_to_quest = "converted_to_quest"
    dismissed = "dismissed"


class MemorySourceType(str, enum.Enum):
    diary = "diary"
    focus_habit = "focus_habit"
    coping_strategy = "coping_strategy"
    preference = "preference"


# ----------------- Core Entities -----------------

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_speed_per_click: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    pets: Mapped[List["Pet"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quests: Mapped[List["Quest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    focus_sessions: Mapped[List["FocusSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    distractions: Mapped[List["DistractionLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    diary_entries: Mapped[List["DiaryEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    memories: Mapped[List["AgentMemory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    map_progressions: Mapped[List["UserMapProgression"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.user_id} {self.username!r}>"


class Pet(Base):
    __tablename__ = "pets"

    pet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    pet_name: Mapped[str] = mapped_column(String(50), nullable=False)
    growth_stage: Mapped[GrowthStage] = mapped_column(
        SAEnum(GrowthStage, name="growth_stage"), nullable=False, default=GrowthStage.egg
    )
    food_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pet_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
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
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_quest_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quests.quest_id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[QuestDifficulty] = mapped_column(
        SAEnum(QuestDifficulty, name="quest_difficulty"), nullable=False, default=QuestDifficulty.easy
    )
    xp_assigned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deadline_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[QuestStatus] = mapped_column(
        SAEnum(QuestStatus, name="quest_status"), nullable=False, default=QuestStatus.incomplete, index=True
    )
    priority: Mapped[QuestPriority] = mapped_column(
        SAEnum(QuestPriority, name="quest_priority"), nullable=False, default=QuestPriority.medium
    )
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_micro_task: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="quests")
    parent_quest: Mapped[Optional["Quest"]] = relationship(
        "Quest", remote_side=[quest_id], back_populates="subtasks"
    )
    subtasks: Mapped[List["Quest"]] = relationship(
        "Quest", back_populates="parent_quest", cascade="all, delete-orphan"
    )
    focus_sessions: Mapped[List["FocusSession"]] = relationship(back_populates="quest")

    def __repr__(self) -> str:
        return f"<Quest {self.quest_id} {self.title!r} status={self.status}>"


# ----------------- Focus Session & Distractions (Focus Agent) -----------------

class FocusSession(Base):
    __tablename__ = "focus_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    quest_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quests.quest_id", ondelete="SET NULL"), nullable=True, index=True
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    actual_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[FocusSessionStatus] = mapped_column(
        SAEnum(FocusSessionStatus, name="focus_session_status"),
        nullable=False,
        default=FocusSessionStatus.started,
        index=True,
    )
    distraction_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    xp_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="focus_sessions")
    quest: Mapped[Optional["Quest"]] = relationship(back_populates="focus_sessions")
    distractions: Mapped[List["DistractionLog"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FocusSession {self.session_id} status={self.status} duration={self.duration_minutes}m>"


class DistractionLog(Base):
    """Park a Thought feature: holds thoughts so users can stay in focus without anxiety."""
    __tablename__ = "distraction_logs"

    log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("focus_sessions.session_id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    thought_content: Mapped[str] = mapped_column(Text, nullable=False)
    action_taken: Mapped[DistractionAction] = mapped_column(
        SAEnum(DistractionAction, name="distraction_action"),
        nullable=False,
        default=DistractionAction.parked,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session: Mapped[Optional["FocusSession"]] = relationship(back_populates="distractions")
    user: Mapped["User"] = relationship(back_populates="distractions")

    def __repr__(self) -> str:
        return f"<DistractionLog {self.log_id} action={self.action_taken}>"


# ----------------- Dear Diary & Vector Memory (Regulate Agent) -----------------

class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    mood_score: Mapped[int] = mapped_column(Integer, nullable=False, default=3)  # 1 (Overwhelmed) to 5 (Great)
    mood_tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_reflection: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="diary_entries")

    def __repr__(self) -> str:
        return f"<DiaryEntry {self.entry_id} mood={self.mood_score}>"


class AgentMemory(Base):
    """Long-term vector memory store using pgvector for RAG contextual retrieval."""
    __tablename__ = "agent_memory"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type: Mapped[MemorySourceType] = mapped_column(
        SAEnum(MemorySourceType, name="memory_source_type"),
        nullable=False,
        default=MemorySourceType.diary,
        index=True,
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(settings.VECTOR_DIMENSION), nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="memories")

    def __repr__(self) -> str:
        return f"<AgentMemory {self.memory_id} source={self.source_type}>"


# ----------------- Fantasy Map Progression -----------------

class MapNode(Base):
    """Nodes along the adventure path on the Journey Map."""
    __tablename__ = "map_nodes"

    node_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rewards_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    progressions: Mapped[List["UserMapProgression"]] = relationship(
        back_populates="node", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MapNode {self.node_id} {self.title!r} required_xp={self.required_xp}>"


class UserMapProgression(Base):
    __tablename__ = "user_map_progression"

    progression_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("map_nodes.node_id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_unlocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    unlocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="map_progressions")
    node: Mapped["MapNode"] = relationship(back_populates="progressions")

    def __repr__(self) -> str:
        return f"<UserMapProgression user={self.user_id} node={self.node_id} completed={self.is_completed}>"
        return f"<Quest {self.quest_id} {self.title!r} status={self.status}>"