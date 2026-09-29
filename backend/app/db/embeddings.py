import uuid
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.db_models import AgentMemory, MemorySourceType


# ----------------- Async Operations (FastAPI) -----------------

async def add_agent_memory(
    db: AsyncSession,
    user_id: uuid.UUID,
    content: str,
    embedding: List[float],
    source_type: MemorySourceType = MemorySourceType.diary,
    source_id: Optional[uuid.UUID] = None,
    metadata_json: Optional[Dict[str, Any]] = None,
) -> AgentMemory:
    """Inserts a new vector memory record for the user."""
    memory = AgentMemory(
        user_id=user_id,
        source_type=source_type,
        source_id=source_id,
        content=content,
        embedding=embedding,
        metadata_json=metadata_json,
    )
    db.add(memory)
    await db.flush()
    await db.refresh(memory)
    return memory


async def search_similar_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    query_embedding: List[float],
    top_k: int = 5,
    min_similarity: float = 0.5,
    source_type: Optional[MemorySourceType] = None,
) -> List[Tuple[AgentMemory, float]]:
    """
    Finds the most relevant past memories using cosine distance.
    Returns a list of (AgentMemory, similarity_score) tuples, where similarity_score = 1.0 - distance.
    """
    distance_col = AgentMemory.embedding.cosine_distance(query_embedding).label("distance")

    filters = [AgentMemory.user_id == user_id]
    if source_type:
        filters.append(AgentMemory.source_type == source_type)

    stmt = (
        select(AgentMemory, distance_col)
        .where(and_(*filters))
        .order_by(distance_col.asc())
        .limit(top_k)
    )

    result = await db.execute(stmt)
    rows = result.all()

    memories_with_similarity = []
    for memory, distance in rows:
        similarity = 1.0 - float(distance) if distance is not None else 0.0
        if similarity >= min_similarity:
            memories_with_similarity.append((memory, round(similarity, 4)))

    return memories_with_similarity


# ----------------- Synchronous Operations (Celery Workers) -----------------

def sync_add_agent_memory(
    db: Session,
    user_id: uuid.UUID,
    content: str,
    embedding: List[float],
    source_type: MemorySourceType = MemorySourceType.diary,
    source_id: Optional[uuid.UUID] = None,
    metadata_json: Optional[Dict[str, Any]] = None,
) -> AgentMemory:
    """Synchronous insertion of vector memory for background Celery tasks."""
    memory = AgentMemory(
        user_id=user_id,
        source_type=source_type,
        source_id=source_id,
        content=content,
        embedding=embedding,
        metadata_json=metadata_json,
    )
    db.add(memory)
    db.flush()
    db.refresh(memory)
    return memory


def sync_search_similar_memories(
    db: Session,
    user_id: uuid.UUID,
    query_embedding: List[float],
    top_k: int = 5,
    min_similarity: float = 0.5,
    source_type: Optional[MemorySourceType] = None,
) -> List[Tuple[AgentMemory, float]]:
    """Synchronous search of similar memories for background Celery tasks."""
    distance_col = AgentMemory.embedding.cosine_distance(query_embedding).label("distance")

    filters = [AgentMemory.user_id == user_id]
    if source_type:
        filters.append(AgentMemory.source_type == source_type)

    stmt = (
        select(AgentMemory, distance_col)
        .where(and_(*filters))
        .order_by(distance_col.asc())
        .limit(top_k)
    )

    result = db.execute(stmt)
    rows = result.all()

    memories_with_similarity = []
    for memory, distance in rows:
        similarity = 1.0 - float(distance) if distance is not None else 0.0
        if similarity >= min_similarity:
            memories_with_similarity.append((memory, round(similarity, 4)))

    return memories_with_similarity
