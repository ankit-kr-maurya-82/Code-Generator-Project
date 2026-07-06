from typing import List, Dict, Any
from collections import Counter
import re

from services.history_service import (
    get_all_conversations,
    get_conversations_by_keyword,
    get_recent_conversations
)


def extract_keywords_from_text(text: str) -> List[str]:
    """Extract important keywords from text."""
    # Remove common words and clean text
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
        'when', 'where', 'why', 'how', 'can', 'may', 'might', 'must', 'shall'
    }
    
    # Extract words (alphanumeric + underscore, case-insensitive)
    words = re.findall(r'\b[a-z0-9_]+\b', text.lower())
    
    # Filter out common words and keep words with 3+ characters
    keywords = [w for w in words if w not in common_words and len(w) >= 3]
    
    return keywords


def get_conversation_topics() -> Dict[str, int]:
    """Analyze all conversations and extract topic frequencies."""
    conversations = get_all_conversations()
    topic_counter = Counter()
    
    for conv in conversations:
        keywords = extract_keywords_from_text(conv.user_prompt)
        topic_counter.update(keywords)
    
    return dict(topic_counter.most_common(15))


def find_relevant_conversations(current_prompt: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Find the most relevant previous conversations for the current prompt."""
    keywords = extract_keywords_from_text(current_prompt)
    
    if not keywords:
        # If no keywords found, return recent conversations
        return format_conversations(get_recent_conversations(limit))
    
    # Search for each keyword and collect results
    relevant_convs = []
    seen_ids = set()
    
    for keyword in keywords[:5]:  # Use top 5 keywords
        matching = get_conversations_by_keyword(keyword)
        for conv in matching:
            if conv.id not in seen_ids:
                relevant_convs.append(conv)
                seen_ids.add(conv.id)
                if len(relevant_convs) >= limit:
                    return format_conversations(relevant_convs[:limit])
    
    # If not enough matches, pad with recent conversations
    if len(relevant_convs) < limit:
        recent = get_recent_conversations(limit * 2)
        for conv in recent:
            if conv.id not in seen_ids:
                relevant_convs.append(conv)
                seen_ids.add(conv.id)
                if len(relevant_convs) >= limit:
                    break
    
    return format_conversations(relevant_convs[:limit])


def format_conversations(conversations: List) -> List[Dict[str, Any]]:
    """Format conversations for display."""
    return [
        {
            "id": conv.id,
            "user_prompt": conv.user_prompt[:200] + ("..." if len(conv.user_prompt) > 200 else ""),
            "ai_response": conv.ai_response[:300] + ("..." if len(conv.ai_response) > 300 else ""),
            "timestamp": conv.timestamp.isoformat()
        }
        for conv in conversations
    ]


def build_context_from_history(current_prompt: str) -> str:
    """Build AI context from conversation history."""
    topics = get_conversation_topics()
    relevant_convs = find_relevant_conversations(current_prompt, limit=3)
    
    if not relevant_convs:
        return "No previous conversation history available."
    
    # Build context string
    context_parts = [
        "Based on previous conversation history, here's what we've been working on:",
        ""
    ]
    
    for i, conv in enumerate(relevant_convs, 1):
        context_parts.append(f"Previous {i}:")
        context_parts.append(f"  User asked: {conv['user_prompt']}")
        context_parts.append(f"  We responded: {conv['ai_response']}")
        context_parts.append("")
    
    if topics:
        context_parts.append("Common topics discussed: " + ", ".join(list(topics.keys())[:5]))
    
    return "\n".join(context_parts)


def get_history_summary() -> Dict[str, Any]:
    """Get a summary of conversation history."""
    conversations = get_all_conversations()
    topics = get_conversation_topics()
    
    return {
        "total_conversations": len(conversations),
        "top_topics": topics,
        "recent_count": min(5, len(conversations)),
        "first_conversation": conversations[0].timestamp.isoformat() if conversations else None,
        "last_conversation": conversations[-1].timestamp.isoformat() if conversations else None
    }
