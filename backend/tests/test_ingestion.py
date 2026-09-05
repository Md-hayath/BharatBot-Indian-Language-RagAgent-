from ingestion.build_vectorstore import ingest_file
import tempfile, os

def test_ingest_txt():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("यह एक परीक्षण है। This is a test document about India.")
        path = f.name
    result = ingest_file(path)
    os.unlink(path)
    assert result > 0