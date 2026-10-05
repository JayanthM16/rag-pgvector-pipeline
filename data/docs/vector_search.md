# Vector Search and RAG

Retrieval-augmented generation, or RAG, improves the answers of a language model by retrieving relevant passages from a knowledge base and adding them to the prompt. A RAG data pipeline loads documents, splits them into chunks, converts each chunk to an embedding vector with an embedding model, and stores the vectors in a vector database.

At query time the question is embedded with the same model, and the database returns the nearest chunks, usually ranked by cosine similarity. Approximate nearest neighbor indexes such as HNSW make this fast on large collections. The pgvector extension adds a vector type and HNSW indexes to PostgreSQL.

Chunk size matters: chunks that are too large dilute the meaning, while chunks that are too small lose context. Overlap between neighboring chunks helps preserve context across boundaries. Retrieval quality is measured with metrics such as recall at k, which checks whether the correct document appears in the top k results, and mean reciprocal rank, which rewards ranking the correct document higher.
