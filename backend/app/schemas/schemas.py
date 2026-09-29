import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Enums (mirror model enums) ----------

class GrowthStage(str, Enum):
    egg = "egg"
    hatchling = "hatchling"
    juvenile = "juvenile"
    adult = "adult"


class PetMood(str, Enum):
    happy = "happy"
    neutral = "neutral"
    sad = "sad"
    hungry = "hungry"


class QuestDifficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    extreme = "extreme"
    extreme_final_boss = "extreme_final_boss"


class QuestStatus(str, Enum):
    incomplete = "incomplete"
    done = "done"


class QuestPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    critical_final_boss = "critical_final_boss"


class FocusSessionStatus(str, Enum):
    started = "started"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"


class DistractionAction(str, Enum):
    parked = "parked"
    converted_to_quest = "converted_to_quest"
    dismissed = "dismissed"


class MemorySourceType(str, Enum):
    diary = "diary"
    focus_habit = "focus_habit"
    coping_strategy = "coping_strategy"
    preference = "preference"


# ---------- User Schemas ----------

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    age: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    avg_speed_per_click: Optional[float] = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    avg_speed_per_click: Optional[float] = None
    created_at: datetime
    updated_at: datetime


# ---------- Pet Schemas ----------

class PetBase(BaseModel):
    pet_name: str = Field(..., min_length=1, max_length=50)
    growth_stage: GrowthStage = GrowthStage.egg
    food_type: Optional[str] = None
    pet_age: Optional[int] = None
    pet_mood: PetMood = PetMood.neutral
    current_xp: int = 0


class PetCreate(PetBase):
    user_id: uuid.UUID


class PetUpdate(BaseModel):
    pet_name: Optional[str] = Field(None, min_length=1, max_length=50)
    growth_stage: Optional[GrowthStage] = None
    food_type: Optional[str] = None
    pet_age: Optional[int] = None
    pet_mood: Optional[PetMood] = None
    current_xp: Optional[int] = None


class PetRead(PetBase):
    model_config = ConfigDict(from_attributes=True)

    pet_id: uuid.UUID
    user_id: uuid.UUID


# ---------- Quest Schemas ----------

class QuestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    difficulty_level: QuestDifficulty = QuestDifficulty.easy
    xp_assigned: int = 0
    estimated_duration_minutes: Optional[int] = None
    deadline_timestamp: Optional[datetime] = None
    status: QuestStatus = QuestStatus.incomplete
    priority: QuestPriority = QuestPriority.medium
    tags: Optional[List[str]] = None
    parent_quest_id: Optional[uuid.UUID] = None
    is_micro_task: bool = False


class QuestCreate(QuestBase):
    user_id: uuid.UUID


class QuestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    difficulty_level: Optional[QuestDifficulty] = None
    xp_assigned: Optional[int] = None
    estimated_duration_minutes: Optional[int] = None
    deadline_timestamp: Optional[datetime] = None
    status: Optional[QuestStatus] = None
    priority: Optional[QuestPriority] = None
    tags: Optional[List[str]] = None
    is_micro_task: Optional[bool] = None


class QuestRead(QuestBase):
    model_config = ConfigDict(from_attributes=True)

    quest_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------- Focus Session & Distraction Schemas (Focus Agent) ----------

class FocusSessionBase(BaseModel):
    duration_minutes: int = Field(default=25, ge=1, le=180)
    quest_id: Optional[uuid.UUID] = None


class FocusSessionCreate(FocusSessionBase):
    user_id: uuid.UUID


class FocusSessionUpdate(BaseModel):
    status: Optional[FocusSessionStatus] = None
    actual_duration_seconds: Optional[int] = None
    distraction_count: Optional[int] = None
    xp_awarded: Optional[int] = None
    ended_at: Optional[datetime] = None


class FocusSessionRead(FocusSessionBase):
    model_config = ConfigDict(from_attributes=True)

    session_id: uuid.UUID
    user_id: uuid.UUID
    actual_duration_seconds: int
    status: FocusSessionStatus
    distraction_count: int
    xp_awarded: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class DistractionLogCreate(BaseModel):
    thought_content: str = Field(..., min_length=1)
    session_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    action_taken: DistractionAction = DistractionAction.parked


class DistractionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: uuid.UUID
    session_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    thought_content: str
    action_taken: DistractionAction
    created_at: datetime


# ---------- Dear Diary & Agent Memory Schemas (Regulate Agent) ----------

class DiaryEntryCreate(BaseModel):
    user_id: uuid.UUID
    mood_score: int = Field(default=3, ge=1, le=5)
    mood_tags: Optional[List[str]] = None
    raw_text: str = Field(..., min_length=1)


class DiaryEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entry_id: uuid.UUID
    user_id: uuid.UUID
    mood_score: int
    mood_tags: Optional[List[str]] = None
    raw_text: str
    ai_reflection: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AgentMemoryCreate(BaseModel):
    user_id: uuid.UUID
    source_type: MemorySourceType = MemorySourceType.diary
    source_id: Optional[uuid.UUID] = None
    content: str
    embedding: List[float]
    metadata_json: Optional[Dict[str, Any]] = None


class AgentMemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    memory_id: uuid.UUID
    user_id: uuid.UUID
    source_type: MemorySourceType
    source_id: Optional[uuid.UUID] = None
    content: str
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class MemorySearchResult(BaseModel):
    memory: AgentMemoryRead
    similarity_score: float


# ---------- Fantasy Map Schemas ----------

class MapNodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    node_id: int
    zone_id: int
    title: str
    description: Optional[str] = None
    required_xp: int
    order_index: int
    rewards_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class UserMapProgressionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    progression_id: uuid.UUID
    user_id: uuid.UUID
    node_id: int
    is_unlocked: bool
    is_completed: bool
    unlocked_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    node: Optional[MapNodeRead] = None