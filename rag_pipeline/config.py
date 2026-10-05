import os
from pathlib import Path

PG_DSN = os.getenv("PG_DSN", "postgresql://rag:rag@localhost:5433/rag")
DOCS_DIR = os.getenv("DOCS_DIR", "data/docs")
EVAL_FILE = os.getenv("EVAL_FILE", "eval/questions.jsonl")
SCHEMA_FILE = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")   # 384-dim; change schema.sql if you change it
EMBED_CACHE = os.getenv("FASTEMBED_CACHE", ".cache/fastembed")
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # recommended for BGE retrieval

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))        # characters
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))  # characters
TOP_K = int(os.getenv("TOP_K", "5"))

MIN_RECALL = float(os.getenv("MIN_RECALL", "0.80"))     # quality gate thresholds
MIN_MRR = float(os.getenv("MIN_MRR", "0.60"))
