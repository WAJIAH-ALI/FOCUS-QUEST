import uuid
from datetime import datetime
from enum import Enum

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
    extreme = "extreme"  # Added an additional difficulty level for demonstration
    extreme_final_boss = "extreme_final_boss"  # Added an additional difficulty level for demonstration


class QuestStatus(str, Enum):
    incomplete = "incomplete"
    done = "done"


class QuestPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"  # Added an additional priority level for demonstration
    critical_final_boss = "critical_final_boss"  # Added an additional priority level for demonstration


# ---------- User ----------

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    age: int | None = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    age: int | None = None
    avg_speed_per_click: float | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    avg_speed_per_click: float | None = None
    created_at: datetime
    updated_at: datetime


# ---------- Pet ----------

class PetBase(BaseModel):
    pet_name: str = Field(..., min_length=1, max_length=50)
    growth_stage: GrowthStage = GrowthStage.egg
    food_type: str | None = None
    pet_age: int | None = None
    pet_mood: PetMood = PetMood.neutral
    current_xp: int = 0


class PetCreate(PetBase):
    user_id: uuid.UUID


class PetUpdate(BaseModel):
    pet_name: str | None = Field(None, min_length=1, max_length=50)
    growth_stage: GrowthStage | None = None
    food_type: str | None = None
    pet_age: int | None = None
    pet_mood: PetMood | None = None
    current_xp: int | None = None


class PetRead(PetBase):
    model_config = ConfigDict(from_attributes=True)

    pet_id: uuid.UUID
    user_id: uuid.UUID


# ---------- Quest ----------

class QuestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    difficulty_level: QuestDifficulty = QuestDifficulty.easy
    xp_assigned: int = 0
    deadline_timestamp: datetime | None = None
    status: QuestStatus = QuestStatus.incomplete
    priority: QuestPriority = QuestPriority.medium


class QuestCreate(QuestBase):
    user_id: uuid.UUID


class QuestUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    difficulty_level: QuestDifficulty | None = None
    xp_assigned: int | None = None
    deadline_timestamp: datetime | None = None
    status: QuestStatus | None = None
    priority: QuestPriority | None = None


class QuestRead(QuestBase):
    model_config = ConfigDict(from_attributes=True)

    quest_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime