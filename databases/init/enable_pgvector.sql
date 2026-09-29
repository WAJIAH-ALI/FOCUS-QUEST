-- databases/init/enable_pgvector.sql
-- Enables UUID and vector extension for FocusQuest

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

