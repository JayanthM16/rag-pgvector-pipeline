from . import config
from .db import connect, vec
from .embeddings import embed_query


def search(question: str, k: int | None = None, conn=None) -> list[dict]:
    """Top-k chunks by cosine similarity (pgvector HNSW index)."""
    k = k or config.TOP_K
    own = conn is None
    conn = conn or connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT doc_id, chunk_index, content, 1 - (embedding <=> %s::vector) AS score
                   FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s""",
                (vec(embed_query(question)),) * 2 + (k,),
            )
            return [dict(doc_id=r[0], chunk_index=r[1], content=r[2], score=float(r[3]))
                    for r in cur.fetchall()]
    finally:
        if own:
            conn.close()
