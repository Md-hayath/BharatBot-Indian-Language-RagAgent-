import os
import re
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File
from api.schemas import UploadResponse
from ingestion.build_vectorstore import ingest_file, load_document
from tools.language_detector import detect_language
from config.settings import DATA_RAW_PATH
from config.languages import get_folder

router = APIRouter()


def _safe_filename(filename: str) -> str:
    name = os.path.basename(filename or "upload")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "upload"


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    safe_name = _safe_filename(file.filename)
    ext = os.path.splitext(safe_name)[1].lower()

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Detect language from the extracted document text, not the filename
        text = load_document(tmp_path)
        lang_result = detect_language(text[:1000])
        lang_folder = get_folder(lang_result["code"])

        save_dir = os.path.join(DATA_RAW_PATH, lang_folder)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, safe_name)
        shutil.move(tmp_path, file_path)
    except Exception:
        os.unlink(tmp_path)
        raise

    chunks_added = ingest_file(file_path, text=text, language=lang_result["code"])

    return UploadResponse(
        message="Document uploaded and indexed successfully",
        chunks_added=chunks_added,
        filename=safe_name
    )