CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    doc_id       TEXT PRIMARY KEY,                 -- relative path of the source file
    content_hash TEXT NOT NULL,                    -- sha256 of the full text (change detection)
    n_chunks     INT  NOT NULL,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id    TEXT PRIMARY KEY,                  -- sha1(doc_id + chunk text): stable, content-addressed
    doc_id      TEXT NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
    chunk_index INT  NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(384) NOT NULL,              -- must match the embedding model's dimension
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS chunks_doc_idx ON chunks (doc_id);
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS ingest_runs (
    run_id         SERIAL PRIMARY KEY,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    docs_seen      INT, docs_changed INT, docs_deleted INT,
    chunks_added   INT, chunks_reused INT, chunks_removed INT,
    seconds        DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS eval_runs (
    run_id        SERIAL PRIMARY KEY,
    ts            TIMESTAMPTZ NOT NULL DEFAULT now(),
    k             INT, n_questions INT,
    recall_at_k   DOUBLE PRECISION,
    mrr           DOUBLE PRECISION,
    passed        BOOLEAN
);
