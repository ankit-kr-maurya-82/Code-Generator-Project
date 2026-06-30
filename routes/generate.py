from fastapi import APIRouter
from schemas.prompt import Prompt
from services.ai_service import generate_code

router = APIRouter()


@router.post("/generate")
async def generate(data: Prompt):

    result = await generate_code(data.prompt)

    return {
        "response": result
    }
