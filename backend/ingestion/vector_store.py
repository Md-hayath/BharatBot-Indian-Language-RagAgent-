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
        _conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                language TEXT,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
    return _conn


def add_chunks(chunks: list, embeddings) -> None:
    conn = get_connection()
    sources = {c["source"] for c in chunks}
    with conn.cursor() as cur:
        # Replace any existing chunks for these filenames instead of piling up
        # duplicates when the same document is re-uploaded.
        for source in sources:
            cur.execute("DELETE FROM document_chunks WHERE source = %s", (source,))
        cur.executemany(
            "INSERT INTO document_chunks (text, source, chunk_id, embedding) VALUES (%s, %s, %s, %s)",
            [(c["text"], c["source"], c["chunk_id"], emb) for c, emb in zip(chunks, embeddings)]
        )


def add_document_record(filename: str, file_path: str, language: str, chunk_count: int) -> None:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (filename, file_path, language, chunk_count, uploaded_at)
            VALUES (%s, %s, %s, %s, now())
            ON CONFLICT (filename) DO UPDATE
            SET file_path = EXCLUDED.file_path,
                language = EXCLUDED.language,
                chunk_count = EXCLUDED.chunk_count,
                uploaded_at = now()
            """,
            (filename, file_path, language, chunk_count)
        )


def search(query_embedding, top_k: int, source: str = None) -> list:
    conn = get_connection()
    with conn.cursor() as cur:
        if source:
            cur.execute(
                "SELECT text, source FROM document_chunks WHERE source = %s ORDER BY embedding <-> %s LIMIT %s",
                (source, query_embedding, top_k)
            )
        else:
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


def list_documents() -> list:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT filename FROM documents ORDER BY uploaded_at DESC")
        return [row[0] for row in cur.fetchall()]
