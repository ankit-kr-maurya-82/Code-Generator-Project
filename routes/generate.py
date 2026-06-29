from fastapi import APIRouter, HTTPException

from schemas.prompt import Prompt
from services.ai_service import AIConfigurationError, AIServiceError, generate_code

router = APIRouter()

@router.post("/generate")
async def generate(data: Prompt):
    try:
        response = await generate_code(data.prompt)
    except AIConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except AIServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return {"response": response}
