"""CLI:  python -m rag_pipeline.query "how does iceberg handle schema changes?" """
import sys

from .retrieve import search

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is a lakehouse?"
    for i, h in enumerate(search(question), 1):
        print(f"\n#{i}  score={h['score']:.3f}  {h['doc_id']} (chunk {h['chunk_index']})")
        print(h["content"][:400].replace("\n", " ") + ("..." if len(h["content"]) > 400 else ""))
