from functools import lru_cache

from . import config


@lru_cache(maxsize=1)
def _model():
    from fastembed import TextEmbedding           # lazy import: keeps unit tests light
    return TextEmbedding(model_name=config.EMBED_MODEL, cache_dir=config.EMBED_CACHE)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return [v.tolist() for v in _model().embed(texts)]


def embed_query(q: str) -> list[float]:
    return embed_texts([config.QUERY_PREFIX + q])[0]
