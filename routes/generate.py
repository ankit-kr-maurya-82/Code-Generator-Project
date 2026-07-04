import os

from fastapi import APIRouter, HTTPException
from schemas.prompt import Prompt
from services.ai_service import AIServiceError, generate_code
from services.prompt_service import build_generation_prompt, has_file
from db import engine
from sqlmodel import Session
from models.history import HistoryItem

router = APIRouter()


@router.post("/generate")
async def generate(data: Prompt):
    has_file_name = bool((data.file_name or "").strip())
    has_file_content = data.file_content is not None
    has_multiple_files = bool(getattr(data, "files", None))
    has_attached_file = has_file_name or has_file_content or has_multiple_files
    has_partial_file_payload = has_attached_file and (has_file_name != has_file_content)

    if has_partial_file_payload:
        raise HTTPException(
            status_code=400,
            detail="Both file_name and file_content are required for file analysis.",
        )

    if has_multiple_files:
        for file in data.files or []:
            file_name = (file.get("name") or "").strip()
            file_extension = os.path.splitext(file_name)[1].lower()
            is_pdf = file_extension == ".pdf"
            is_text_file = file_extension in {
                ".txt",
                ".md",
                ".py",
                ".js",
                ".ts",
                ".tsx",
                ".jsx",
                ".html",
                ".css",
                ".json",
                ".csv",
                ".xml",
                ".yaml",
                ".yml",
                ".java",
                ".c",
                ".cpp",
                ".cs",
                ".php",
                ".rb",
                ".go",
                ".rs",
                ".sql",
                ".env",
            }

            if not is_pdf and not is_text_file:
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF and text files are supported for analysis.",
                )
    elif has_file_name or has_file_content:
        file_name = (data.file_name or "").strip()
        file_extension = os.path.splitext(file_name)[1].lower()
        is_pdf = file_extension == ".pdf"
        is_text_file = file_extension in {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".html",
            ".css",
            ".json",
            ".csv",
            ".xml",
            ".yaml",
            ".yml",
            ".java",
            ".c",
            ".cpp",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".sql",
            ".env",
        }

        if not is_pdf and not is_text_file:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and text files are supported for analysis.",
            )

    prompt = build_generation_prompt(data)

    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt or attached file content is required.",
        )

    try:
        result = await generate_code(prompt)
    except AIServiceError as error:
        raise HTTPException(status_code=400, detail=str(error))

    # Persist the generation to the database (best-effort)
    try:
        with Session(engine) as session:
            item = HistoryItem(prompt=prompt, response=result)
            session.add(item)
            session.commit()
    except Exception:
        # don't fail the request if DB write fails
        pass

    return {
        "response": result,
        "mode": "file_analysis" if has_file(data) else "prompt",
    }
