# FocusQuest — System Architecture

## Overview

FocusQuest is an AI-powered productivity/gamification app for people who struggle with attention. It combines a Flutter client, a FastAPI backend orchestrating three specialized agents, an async LLM/task pipeline, and a Postgres + pgvector store for user state and long-term agent memory.

## High-Level Diagram (component map)

```
Flutter App ── REST/WebSocket ──▶ FastAPI Backend ──▶ Postgres + pgvector
     │                                  │                  (user state,
     └── Supabase/Firebase ──▶ Auth Layer                   embeddings)
                                        │
                                  Agent Router
                                  ┌──────┼──────┐
                              Capture  Focus  Regulate
                                  │      │      │
                                  └──────┼──────┘
                                         ▼
                              Celery Task Queue ◀──▶ Redis Broker
                                         │
                                         ▼
                                  LLM Calls (async)
                                         │
                                         ▼
                              Postgres + pgvector (embeddings)
```

## Components

### A. Flutter App (Frontend)
- Cross-platform client (iOS/Android/web) built in Flutter/Dart.
- Talks to the backend over REST for standard requests and WebSocket for streaming/real-time agent responses.
- Authenticates directly against the Auth Layer (Supabase/Firebase) and attaches the resulting session token to backend calls.
- Hosts the fantasy map UI, pet companion system, and the "Dear Diary" screen.

### B. FastAPI Backend
- Single entrypoint for all client traffic (REST + WebSocket).
- Validates auth tokens, then routes requests into the Agent Router.
- Owns the Postgres connection pool and Celery task dispatch.
- Stateless at the process level — all durable state lives in Postgres; all queued work lives in Redis/Celery.

### C. Auth Layer (Supabase/Firebase)
- Handles signup/login, session/token issuance, and password/OAuth flows.
- Decoupled from the FastAPI backend: the Flutter app talks to it directly for auth, and the backend only verifies tokens (does not proxy auth traffic).

### D. Agent Router
- Inspects each incoming request (or task) and dispatches it to the correct agent: Capture, Focus, or Regulate.
- Routing logic can be intent-based (NLP classification) or explicit (client specifies mode).
- Central place to add cross-agent concerns: rate limiting, logging, fallback handling.

### E. Capture Agent
- Handles quick-capture of tasks/thoughts/braindumps from the user.
- Normalizes raw input into structured tasks written to the Celery queue for processing (e.g., tagging, prioritization via LLM).

### F. Focus Agent
- Manages active focus sessions — session start/stop, nudges, gamified rewards tied to the fantasy map and pet companion.
- Reads/writes session state to Postgres; may trigger LLM calls for personalized encouragement.

### G. Regulate Agent
- Supports emotional/attention regulation — check-ins, the "Dear Diary" reflection flow, coping prompts.
- Heaviest user of pgvector embeddings, since diary entries and past regulation context are retrieved by similarity search for continuity.

### H. Celery Task Queue + Worker
- All agent work that involves an LLM call or other slow I/O is pushed here rather than blocking the request/response cycle.
- Worker pulls tasks off the queue, executes them (including calling out to LLMs), and writes results back to Postgres.

### I. Redis Broker
- Message broker for Celery (task queue storage, result backend optionally).
- Also usable for lightweight caching (session data, rate-limit counters) if needed later.

### J. LLM Calls (async)
- Celery workers make async calls out to LLM providers (OpenAI, Anthropic, etc.) for generation, classification, and embedding tasks.
- Isolated in its own client module so providers/models can be swapped without touching agent logic.

### K–M. Postgres + pgvector
- **L. User state/history** — structured relational data: users, tasks, sessions, streaks, pet/map progression.
- **M. Embeddings (AI diary, agent memory)** — vector column(s) via pgvector, storing embeddings of diary entries and agent memory for similarity search/retrieval-augmented context.
- Single database instance keeps relational and vector data joinable (e.g., pull a user's diary embeddings alongside their profile in one query).

## Data Flow (typical request)

1. User acts in the Flutter app (e.g., logs a task) → REST/WebSocket call to FastAPI, with an auth token from Supabase/Firebase.
2. FastAPI verifies the token, passes the request to the Agent Router.
3. Agent Router dispatches to Capture/Focus/Regulate based on intent.
4. Agent does any fast, synchronous work directly against Postgres; anything requiring an LLM call is pushed onto the Celery queue via Redis.
5. Celery worker picks up the task, calls the LLM asynchronously, and writes the result (plus any new embeddings) back to Postgres.
6. FastAPI streams the result back to the Flutter app over WebSocket, or the client polls/refetches over REST.

## Key Design Decisions

- **Async LLM calls are queued, not inline** — keeps API response times fast and avoids blocking on provider latency/rate limits.
- **Single Postgres instance for both relational and vector data** — avoids running a separate vector DB; pgvector keeps everything joinable and reduces infra surface area for a solo/small-team project.
- **Auth is delegated, not reimplemented** — Supabase/Firebase handles the hard parts of auth; the backend only verifies.
- **Three agents are separate modules, not one monolithic prompt** — allows independent iteration on Capture/Focus/Regulate prompts, models, and logic.

## Open Questions / Future Considerations

- Whether Celery result backend should also live in Redis or write straight to Postgres.
- Caching strategy for frequently-read user state (Redis as cache vs. broker-only).
- Multi-model routing in the LLM layer if different agents benefit from different providers/models.