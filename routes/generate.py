import os

from fastapi import APIRouter, HTTPException
from schemas.prompt import Prompt
from services.ai_service import AIServiceError, generate_code
from services.prompt_service import build_generation_prompt, has_file
from services.history_service import add_conversation
from services.history_analysis import build_context_from_history

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
        # Build context from conversation history
        history_context = build_context_from_history(prompt)
        
        # Generate code with historical context
        result = await generate_code(prompt, history_context)
        
        # Store this conversation in history
        add_conversation(
            user_prompt=data.prompt,
            ai_response=result,
            file_name=data.file_name,
            file_content=data.file_content[:500] if data.file_content else None,  # Store first 500 chars
            tags=["code_generation", "file_analysis" if has_file(data) else "prompt"]
        )
    except AIServiceError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "response": result,
        "mode": "file_analysis" if has_file(data) else "prompt",
    }


@router.get("/history")
async def get_history(limit: int = 10):
    """Get recent conversation history."""
    from services.history_service import get_recent_conversations
    
    conversations = get_recent_conversations(limit)
    return {
        "conversations": [
            {
                "id": conv.id,
                "user_prompt": conv.user_prompt[:200],
                "ai_response": conv.ai_response[:200],
                "timestamp": conv.timestamp.isoformat(),
                "tags": conv.tags
            }
            for conv in conversations
        ],
        "count": len(conversations)
    }


@router.get("/history/stats")
async def get_history_stats():
    """Get statistics and analysis of conversation history."""
    from services.history_analysis import get_history_summary
    
    return get_history_summary()


@router.get("/history/search")
async def search_history(keyword: str):
    """Search conversation history by keyword."""
    from services.history_service import get_conversations_by_keyword
    
    if not keyword.strip():
        raise HTTPException(
            status_code=400,
            detail="Keyword is required for search."
        )
    
    conversations = get_conversations_by_keyword(keyword)
    return {
        "keyword": keyword,
        "conversations": [
            {
                "id": conv.id,
                "user_prompt": conv.user_prompt[:200],
                "ai_response": conv.ai_response[:200],
                "timestamp": conv.timestamp.isoformat()
            }
            for conv in conversations
        ],
        "count": len(conversations)
    }


@router.post("/history/clear")
async def clear_history():
    """Clear all conversation history."""
    from services.history_service import clear_history as clear_all
    
    clear_all()
    return {
        "message": "Conversation history cleared successfully.",
        "status": "success"
    }
