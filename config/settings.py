import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
SARVAM_MODEL = "sarvam-30b"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "data", "vector_store")

INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.faiss")
META_FILE = os.path.join(VECTOR_STORE_PATH, "index.pkl")