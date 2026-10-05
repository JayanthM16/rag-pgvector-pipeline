"""Pure retrieval metrics (no I/O) so they are trivially unit-testable."""


def reciprocal_rank(expected: str, ranked_docs: list[str]) -> float:
    for i, d in enumerate(ranked_docs, start=1):
        if d == expected:
            return 1.0 / i
    return 0.0


def hit(expected: str, ranked_docs: list[str]) -> bool:
    return expected in ranked_docs


def aggregate(results: list[tuple[str, list[str]]]) -> dict:
    """results = [(expected_doc, ranked_unique_docs), ...]"""
    n = len(results)
    if n == 0:
        return {"n": 0, "recall_at_k": 0.0, "mrr": 0.0}
    return {
        "n": n,
        "recall_at_k": sum(hit(e, r) for e, r in results) / n,
        "mrr": sum(reciprocal_rank(e, r) for e, r in results) / n,
    }
