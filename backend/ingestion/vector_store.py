import psycopg
from pgvector.psycopg import register_vector
from config.settings import DATABASE_URL, EMBEDDING_DIM

_conn = None


def get_connection():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg.connect(DATABASE_URL, autocommit=True)
        _conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(_conn)
        _conn.execute(f"""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                source TEXT NOT NULL,
                chunk_id INTEGER NOT NULL,
                embedding VECTOR({EMBEDDING_DIM}) NOT NULL
            )
        """)
        _conn.execute("""
            CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
            ON document_chunks USING hnsw (embedding vector_l2_ops)
        """)
    return _conn


def add_chunks(chunks: list, embeddings) -> None:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO document_chunks (text, source, chunk_id, embedding) VALUES (%s, %s, %s, %s)",
            [(c["text"], c["source"], c["chunk_id"], emb) for c, emb in zip(chunks, embeddings)]
        )


def search(query_embedding, top_k: int) -> list:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT text, source FROM document_chunks ORDER BY embedding <-> %s LIMIT %s",
            (query_embedding, top_k)
        )
        return cur.fetchall()


def has_documents() -> bool:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT EXISTS (SELECT 1 FROM document_chunks LIMIT 1)")
        return cur.fetchone()[0]
