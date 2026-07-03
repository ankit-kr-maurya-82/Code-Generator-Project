from fastapi import APIRouter, HTTPException
from schemas.prompt import Prompt
from services.ai_service import AIServiceError, generate_code
from services.prompt_service import build_generation_prompt, has_file

router = APIRouter()


@router.post("/generate")
async def generate(data: Prompt):
    prompt = build_generation_prompt(data)

    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt or attached file content is required.",
        )

    if bool(data.file_name) != bool(data.file_content):
        raise HTTPException(
            status_code=400,
            detail="Both file_name and file_content are required for file analysis.",
        )

    try:
        result = await generate_code(prompt)
    except AIServiceError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "response": result,
        "mode": "file_analysis" if has_file(data) else "prompt",
    }
