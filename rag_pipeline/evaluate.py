"""Retrieval evaluation + quality gate. Exits non-zero (and the Airflow task fails) if below thresholds."""
import json
import sys
from pathlib import Path

from . import config
from .db import connect, init_schema
from .metrics import aggregate
from .retrieve import search


def run_eval(k: int | None = None) -> dict:
    k = k or config.TOP_K
    questions = [json.loads(l) for l in Path(config.EVAL_FILE).read_text().splitlines() if l.strip()]
    conn = connect()
    try:
        init_schema(conn)
        results = []
        for q in questions:
            ranked: list[str] = []
            for hit in search(q["question"], k, conn):
                if hit["doc_id"] not in ranked:           # chunk hits -> unique ranked documents
                    ranked.append(hit["doc_id"])
            results.append((q["expected_doc"], ranked))
        m = aggregate(results)
        m["k"] = k
        m["passed"] = m["recall_at_k"] >= config.MIN_RECALL and m["mrr"] >= config.MIN_MRR
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO eval_runs (k, n_questions, recall_at_k, mrr, passed) VALUES (%s,%s,%s,%s,%s)",
                (k, m["n"], m["recall_at_k"], m["mrr"], m["passed"]),
            )
        conn.commit()
    finally:
        conn.close()
    print(f"eval: recall@{k}={m['recall_at_k']:.3f}  MRR={m['mrr']:.3f}  "
          f"n={m['n']}  gate={'PASS' if m['passed'] else 'FAIL'} "
          f"(min recall {config.MIN_RECALL}, min MRR {config.MIN_MRR})")
    return m


if __name__ == "__main__":
    sys.exit(0 if run_eval()["passed"] else 1)
