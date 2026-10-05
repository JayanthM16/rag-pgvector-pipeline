import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag_pipeline.chunking import split_text
from rag_pipeline.metrics import aggregate, reciprocal_rank

LONG = "\n\n".join(f"Paragraph {i}. " + ("Data engineering moves and models data. " * 12) for i in range(12))


def test_chunks_respect_size_plus_overlap():
    chunks = split_text(LONG, size=800, overlap=120)
    assert len(chunks) > 1
    assert all(0 < len(c) <= 800 + 120 + 2 for c in chunks)


def test_deterministic():
    assert split_text(LONG, 800, 120) == split_text(LONG, 800, 120)


def test_overlap_shared_between_neighbors():
    chunks = split_text(LONG, size=800, overlap=120)
    tail_word = chunks[0].split()[-1]
    assert tail_word in chunks[1][:200]


def test_oversized_paragraph_is_split():
    chunks = split_text("word " * 2000, size=500, overlap=50)
    assert all(len(c) <= 500 + 50 + 2 for c in chunks)


def test_empty_text():
    assert split_text("   \n\n  ") == []


def test_reciprocal_rank():
    assert reciprocal_rank("a", ["b", "a"]) == 0.5
    assert reciprocal_rank("a", ["b", "c"]) == 0.0


def test_aggregate():
    m = aggregate([("a", ["a"]), ("b", ["x", "b"]), ("c", ["x", "y"])])
    assert abs(m["recall_at_k"] - 2 / 3) < 1e-9
    assert abs(m["mrr"] - (1 + 0.5 + 0) / 3) < 1e-9
