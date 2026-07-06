import json
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import uuid

from models.conversation import Conversation, ConversationHistory


HISTORY_FILE = "data/conversation_history.json"


def ensure_history_file_exists():
    """Create history file if it doesn't exist."""
    Path("data").mkdir(exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        history = ConversationHistory()
        with open(HISTORY_FILE, "w") as f:
            json.dump(history.model_dump(mode="json"), f, indent=2, default=str)


def load_history() -> ConversationHistory:
    """Load conversation history from file."""
    ensure_history_file_exists()
    
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
        
        # Parse conversations with proper datetime
        conversations = []
        for conv in data.get("conversations", []):
            conv["timestamp"] = datetime.fromisoformat(conv["timestamp"])
            conversations.append(Conversation(**conv))
        
        return ConversationHistory(
            conversations=conversations,
            total_count=len(conversations)
        )
    except (json.JSONDecodeError, ValueError):
        return ConversationHistory()


def save_history(history: ConversationHistory):
    """Save conversation history to file."""
    ensure_history_file_exists()
    with open(HISTORY_FILE, "w") as f:
        json.dump(history.model_dump(mode="json"), f, indent=2, default=str)


def add_conversation(user_prompt: str, ai_response: str, file_name: Optional[str] = None, 
                    file_content: Optional[str] = None, tags: Optional[List[str]] = None) -> Conversation:
    """Add a new conversation to history."""
    history = load_history()
    
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_prompt=user_prompt,
        ai_response=ai_response,
        file_name=file_name,
        file_content=file_content,
        tags=tags or []
    )
    
    history.conversations.append(conversation)
    history.total_count = len(history.conversations)
    save_history(history)
    
    return conversation


def get_recent_conversations(limit: int = 10) -> List[Conversation]:
    """Get the most recent conversations."""
    history = load_history()
    return sorted(
        history.conversations,
        key=lambda x: x.timestamp,
        reverse=True
    )[:limit]


def get_conversations_by_keyword(keyword: str) -> List[Conversation]:
    """Search conversations by keyword in prompts or responses."""
    history = load_history()
    keyword_lower = keyword.lower()
    
    return [
        conv for conv in history.conversations
        if keyword_lower in conv.user_prompt.lower() or keyword_lower in conv.ai_response.lower()
    ]


def get_all_conversations() -> List[Conversation]:
    """Get all conversations."""
    history = load_history()
    return history.conversations


def clear_history():
    """Clear all conversation history."""
    history = ConversationHistory()
    save_history(history)
