from fastapi import APIRouter

from schemas.prompt import Prompt

router = APIRouter()

@router.post("/generate")
async def generate(data: Prompt):
    return {
        "response": f"You asked: {data.prompt}"
    }
