from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path
from src.rag import ingest_file

router = APIRouter(prefix="/rag", tags=["rag"])

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    dest = UPLOAD_DIR / file.filename

    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_file(str(dest))

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_added": result["added"]
    }
    """    Load file at path, split into chunks, and add to Chroma.
    """