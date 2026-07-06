from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Single message in conversation history."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    """Complete conversation with history."""
    id: str
    user_prompt: str
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    file_name: Optional[str] = None
    file_content: Optional[str] = None
    tags: List[str] = []  # For categorizing conversations
    
    
class ConversationHistory(BaseModel):
    """Wrapper for conversation history."""
    conversations: List[Conversation] = []
    total_count: int = 0
