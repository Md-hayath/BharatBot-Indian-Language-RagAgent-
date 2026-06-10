import os
import shutil
from fastapi import APIRouter, UploadFile, File
from api.schemas import UploadResponse
from ingestion.build_vectorstore import ingest_file
from tools.language_detector import detect_language
from config.settings import DATA_RAW_PATH
from config.languages import get_folder

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    # Read file content to detect language
    content = await file.read()

    # Try to detect language from filename or first bytes
    # Save to appropriate language folder
    sample_text = file.filename
    lang_result = detect_language(sample_text)
    lang_folder = get_folder(lang_result["code"])

    save_dir = os.path.join(DATA_RAW_PATH, lang_folder)
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    chunks_added = ingest_file(file_path)

    return UploadResponse(
        message="Document uploaded and indexed successfully",
        chunks_added=chunks_added,
        filename=file.filename
    )