# Incremental RAG Data Pipeline (pgvector + Airflow + Retrieval Quality Gate)

Document ingestion → chunking → embeddings → **PostgreSQL/pgvector** (HNSW), orchestrated by **Airflow**,
with **change detection at document and chunk level** (only new chunks are embedded) and an automated
**retrieval-quality gate** (recall@k, MRR) that fails the DAG when quality drops.

```
 data/docs/*.md|txt ──▶ detect changes ──▶ chunk ──▶ embed (only NEW chunks) ──▶ pgvector (HNSW, cosine)
   (sha256 per file)    (doc + chunk hash)  (800 chars, 120 overlap)  (BGE-small, 384-d)        │
                                                                                                ▼
                                   eval/questions.jsonl ──▶ recall@k + MRR ──▶ gate (fail DAG if below threshold)
```

## Quick start

```bash
# Option A: everything in Docker (pgvector + Airflow)
make up                                 # UI: http://localhost:8080
docker compose logs airflow | grep -i password     # admin password (user: admin)
# In the UI: unpause DAG `rag_ingest` and trigger it. First run downloads the embedding model (~130 MB).

# Option B: run from your laptop (Python 3.10+)
docker compose up -d vectordb
pip install -r requirements.txt
make ingest          # embeds the 5 sample docs
make eval            # recall@k / MRR + gate
make query Q="what is hidden partitioning?"
make test            # unit tests for chunking + metrics (no DB needed)
```

## See the incremental behavior (screenshot-worthy)

1. `make ingest` → `chunks_added=N, chunks_reused=0`.
2. `make ingest` again → `docs_changed=0, chunks_added=0` (nothing re-embedded).
3. Edit one paragraph in `data/docs/iceberg.md`, `make ingest` → only the changed chunk(s) are embedded; the rest are reused.
4. Delete a file, `make ingest` → `docs_deleted=1`, its chunks vanish (FK cascade).
5. Inspect history: `SELECT * FROM ingest_runs ORDER BY run_id DESC;` and `SELECT * FROM eval_runs;`

## Design decisions (good interview material)

| Decision | Why |
|---|---|
| **Content-addressed chunk ids** (`sha1(doc_id + text)`) | Re-embedding is the expensive step; unchanged chunks are never recomputed. |
| **Per-document transactions** | A crash never leaves a doc half-indexed; reruns are idempotent. |
| **HNSW + cosine** | Fast approximate search with good recall; `vector(384)` must match the model dimension. |
| **Paragraph-aware chunking with overlap** | Keeps semantic units together and preserves context across chunk boundaries. |
| **Query prefix for BGE** | The model was trained with an instruction prefix for retrieval queries; improves recall. |
| **Quality gate in the DAG** | Treats retrieval quality like data quality: a bad chunking/model change fails the run instead of silently degrading answers. |
| **Eval set in git** | Reproducible, reviewable regression tests for retrieval. |

## Metrics to capture for your resume (run, then fill in real numbers)

* **Embedding savings:** after editing 1 of N docs, `chunks_reused / (chunks_reused + chunks_added)` from `ingest_runs`.
* **Retrieval quality:** `recall@5` and `MRR` from `eval_runs` on **your own** corpus + ≥50 questions (the 14 sample questions are only a smoke test).
* **Latency:** time `make query` / `retrieve.search` p50/p95 over ~100 queries.
* **Ablation (strong signal):** compare chunk size 400 vs 800 vs 1200 and overlap 0 vs 120 using `CHUNK_SIZE=... make ingest eval`; report the best config and the delta.

## Scale it up (do at least one so the project isn't a toy)

* Replace the sample docs with a real corpus: Apache Spark / Airflow / dbt docs (Markdown), or your own notes. Aim for 500+ documents.
* Add PDF support (`pypdf`) in `ingest.load_docs`.
* Add hybrid search (Postgres full-text `tsvector` + vector, reciprocal rank fusion) and compare MRR.
* Add a generation step (any LLM) plus answer-faithfulness checks; keep the retrieval gate as is.

## Limitations

* `.md`/`.txt` only; character-based chunking (no tokenizer-aware splitting).
* Retrieval is evaluated at document level against a small hand-labeled set.
* Airflow `standalone` (SQLite, sequential executor) is for local demos, not production.
