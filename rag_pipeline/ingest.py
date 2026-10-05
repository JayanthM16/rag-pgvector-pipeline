"""
Incremental document -> chunk -> embed -> pgvector pipeline.

Incremental at two levels:
  1. Document level : sha256 of the file; unchanged files are skipped entirely.
  2. Chunk level    : chunk_id = sha1(doc_id + text). For a changed document only NEW chunks are
                      embedded; unchanged chunks are reused; chunks that disappeared are deleted.
Deleted source files are removed from the index (ON DELETE CASCADE removes their chunks).
Each document is processed in its own transaction, so a failure never leaves a half-written doc.
"""
import hashlib
import time
from pathlib import Path

from psycopg2.extras import execute_batch, execute_values

from . import config
from .chunking import split_text
from .db import connect, init_schema, vec
from .embeddings import embed_texts

SUPPORTED = {".md", ".txt"}


def load_docs(docs_dir: str):
    root = Path(docs_dir)
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED:
            yield str(p.relative_to(root)), p.read_text(encoding="utf-8")


def _chunk_ids(doc_id: str, text: str) -> dict[str, tuple[int, str]]:
    chunks = split_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    out: dict[str, tuple[int, str]] = {}
    for i, c in enumerate(chunks):
        cid = hashlib.sha1(f"{doc_id}\x00{c}".encode()).hexdigest()
        out.setdefault(cid, (i, c))                      # identical repeated chunk -> keep first
    return out


def run(docs_dir: str | None = None) -> dict:
    docs_dir = docs_dir or config.DOCS_DIR
    t0 = time.time()
    stats = dict(docs_seen=0, docs_changed=0, docs_deleted=0,
                 chunks_added=0, chunks_reused=0, chunks_removed=0)
    conn = connect()
    try:
        init_schema(conn)
        cur = conn.cursor()
        cur.execute("SELECT doc_id, content_hash FROM documents")
        existing = dict(cur.fetchall())
        seen: set[str] = set()

        for doc_id, text in load_docs(docs_dir):
            seen.add(doc_id)
            stats["docs_seen"] += 1
            h = hashlib.sha256(text.encode()).hexdigest()
            if existing.get(doc_id) == h:
                continue                                  # unchanged document

            stats["docs_changed"] += 1
            new = _chunk_ids(doc_id, text)
            cur.execute("SELECT chunk_id FROM chunks WHERE doc_id = %s", (doc_id,))
            old = {r[0] for r in cur.fetchall()}

            to_add = [cid for cid in new if cid not in old]
            to_del = list(old - set(new))
            reused = [cid for cid in new if cid in old]

            vectors = embed_texts([new[cid][1] for cid in to_add])   # only new chunks cost compute

            cur.execute(
                """INSERT INTO documents (doc_id, content_hash, n_chunks, ingested_at)
                   VALUES (%s, %s, %s, now())
                   ON CONFLICT (doc_id) DO UPDATE
                   SET content_hash = EXCLUDED.content_hash, n_chunks = EXCLUDED.n_chunks, ingested_at = now()""",
                (doc_id, h, len(new)),
            )
            if to_add:
                execute_values(
                    cur,
                    "INSERT INTO chunks (chunk_id, doc_id, chunk_index, content, embedding) VALUES %s "
                    "ON CONFLICT (chunk_id) DO NOTHING",
                    [(cid, doc_id, new[cid][0], new[cid][1], vec(v)) for cid, v in zip(to_add, vectors)],
                    template="(%s, %s, %s, %s, %s::vector)",
                )
            if reused:                                    # keep chunk_index aligned with new layout
                execute_batch(cur, "UPDATE chunks SET chunk_index = %s WHERE chunk_id = %s",
                              [(new[cid][0], cid) for cid in reused])
            if to_del:
                cur.execute("DELETE FROM chunks WHERE chunk_id = ANY(%s)", (to_del,))
            conn.commit()

            stats["chunks_added"] += len(to_add)
            stats["chunks_reused"] += len(reused)
            stats["chunks_removed"] += len(to_del)

        gone = [d for d in existing if d not in seen]
        if gone:
            cur.execute("DELETE FROM documents WHERE doc_id = ANY(%s)", (gone,))
            stats["docs_deleted"] = len(gone)

        stats["seconds"] = round(time.time() - t0, 2)
        cur.execute(
            """INSERT INTO ingest_runs (docs_seen, docs_changed, docs_deleted, chunks_added,
                                        chunks_reused, chunks_removed, seconds)
               VALUES (%(docs_seen)s, %(docs_changed)s, %(docs_deleted)s, %(chunks_added)s,
                       %(chunks_reused)s, %(chunks_removed)s, %(seconds)s)""",
            stats,
        )
        conn.commit()
    finally:
        conn.close()
    print(f"ingest: {stats}")
    return stats


if __name__ == "__main__":
    run()
