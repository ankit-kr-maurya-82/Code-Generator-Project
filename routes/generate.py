from fastapi import APIRouter, HTTPException
from schemas.prompt import Prompt
from services.ai_service import AIServiceError, generate_code

router = APIRouter()


@router.post("/generate")
async def generate(data: Prompt):

    try:
        result = await generate_code(data.prompt)
    except AIServiceError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "response": result
    }
