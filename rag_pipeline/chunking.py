"""Paragraph-aware chunker with character overlap. Deterministic (same input -> same chunks)."""
import re


def _hard_split(text: str, size: int) -> list[str]:
    """Split an oversized paragraph on sentence boundaries, slicing only as a last resort."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out, cur = [], ""
    for s in sentences:
        while len(s) > size:                                   # single sentence longer than size
            if cur:
                out.append(cur)
                cur = ""
            out.append(s[:size])
            s = s[size:]
        if not cur:
            cur = s
        elif len(cur) + 1 + len(s) <= size:
            cur += " " + s
        else:
            out.append(cur)
            cur = s
    if cur:
        out.append(cur)
    return out


def _overlap_tail(chunk: str, overlap: int) -> str:
    if overlap <= 0:
        return ""
    tail = chunk[-overlap:]
    if " " in tail:                                            # start on a word boundary
        tail = tail[tail.index(" ") + 1:]
    return tail


def split_text(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    """Chunks are <= size (+ overlap for every chunk after the first)."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces: list[str] = []
    for p in paragraphs:
        pieces.extend(_hard_split(p, size) if len(p) > size else [p])

    chunks: list[str] = []
    cur = ""
    for piece in pieces:
        if not cur:
            cur = piece
        elif len(cur) + 2 + len(piece) <= size:
            cur += "\n\n" + piece
        else:
            chunks.append(cur)
            tail = _overlap_tail(cur, overlap)
            cur = f"{tail}\n\n{piece}" if tail else piece
    if cur:
        chunks.append(cur)
    return chunks
