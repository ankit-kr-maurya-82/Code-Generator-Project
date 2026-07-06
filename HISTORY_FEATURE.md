# Conversation History & Analysis Feature

## Overview

This feature automatically tracks all user prompts and AI responses, analyzes them to extract patterns and topics, and uses that analysis to provide better contextual responses to future questions.

## How It Works

### 1. **Automatic Conversation Storage**
- Every time a user submits a prompt and gets a response, both are automatically stored in `data/conversation_history.json`
- The system stores:
  - User prompt
  - AI response  
  - Timestamp
  - File name (if file was analyzed)
  - Tags (e.g., "code_generation", "file_analysis")

### 2. **History Analysis**
When a new question comes in:
- System extracts keywords from the user's prompt
- Finds the 3 most relevant previous conversations based on keyword matching
- Creates a context summary from these relevant conversations
- Passes this context to the AI service

### 3. **Improved Responses**
- The AI service receives the historical context
- It uses this to maintain consistency and provide more contextual responses
- The AI is explicitly instructed to consider the conversation history

## API Endpoints

### Generate Code (Main Endpoint)
```
POST /generate
```
**Request:**
```json
{
  "prompt": "Generate a function to sort a list",
  "file_name": null,
  "file_content": null,
  "files": null
}
```

**Response:**
```json
{
  "response": "Result...\nCode...\nExplanation...",
  "mode": "prompt"
}
```

### Get Recent History
```
GET /history?limit=10
```
Returns the 10 most recent conversations with prompts and responses.

**Response:**
```json
{
  "conversations": [
    {
      "id": "uuid",
      "user_prompt": "first 200 chars...",
      "ai_response": "first 200 chars...",
      "timestamp": "2024-01-15T10:30:00",
      "tags": ["code_generation", "prompt"]
    }
  ],
  "count": 10
}
```

### Get History Statistics
```
GET /history/stats
```
Returns analytics about conversation patterns, top topics, and frequency.

**Response:**
```json
{
  "total_conversations": 25,
  "top_topics": {
    "python": 12,
    "function": 8,
    "string": 6,
    "list": 5,
    "dict": 4
  },
  "recent_count": 5,
  "first_conversation": "2024-01-10T09:00:00",
  "last_conversation": "2024-01-15T10:30:00"
}
```

### Search History
```
GET /history/search?keyword=python
```
Search through all conversations by keyword.

**Response:**
```json
{
  "keyword": "python",
  "conversations": [
    {
      "id": "uuid",
      "user_prompt": "first 200 chars...",
      "ai_response": "first 200 chars...",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "count": 5
}
```

### Clear History
```
POST /history/clear
```
Completely clears all conversation history.

**Response:**
```json
{
  "message": "Conversation history cleared successfully.",
  "status": "success"
}
```

## Files Modified/Created

### New Files:
1. **models/conversation.py** - Data models for conversations
2. **services/history_service.py** - Stores and retrieves conversations from file
3. **services/history_analysis.py** - Analyzes history and extracts context

### Modified Files:
1. **services/ai_service.py** - Updated to accept and use historical context
2. **routes/generate.py** - Updated to use history and store conversations

## Data Storage

History is stored in `data/conversation_history.json` with the following structure:
```json
{
  "conversations": [
    {
      "id": "unique-uuid",
      "user_prompt": "user's question",
      "ai_response": "AI's response",
      "timestamp": "2024-01-15T10:30:00",
      "file_name": null,
      "file_content": null,
      "tags": ["code_generation"]
    }
  ],
  "total_count": 1
}
```

## Key Features

✅ **Automatic Storage** - No extra work needed; history is stored automatically  
✅ **Context-Aware Responses** - AI considers previous conversations  
✅ **Topic Analysis** - System identifies and tracks common topics discussed  
✅ **Search Capability** - Find previous conversations by keywords  
✅ **Statistics** - View conversation frequency and topic patterns  
✅ **Easy Clearing** - Clear entire history when needed  
✅ **File Support** - Stores file information for reference  

## Example Workflow

1. User asks: "How do I sort a list in Python?"
   - Response is generated and stored with tags ["code_generation"]

2. User asks: "What about dictionaries?"
   - System finds previous "sort" conversation
   - Provides context about lists to make response more coherent
   - Maintains consistent explanation style

3. Later, user asks: "Show me a function that combines lists"
   - System finds both previous conversations
   - AI maintains consistency with previous sorting examples
   - Response is more contextual and consistent

## Backend Architecture

```
User Request
    ↓
build_context_from_history(prompt)
    ├─ extract_keywords(prompt)
    ├─ find_relevant_conversations(keywords)
    └─ format_context_string()
    ↓
generate_code(prompt, history_context)
    ├─ get_system_prompt(prompt, history_context)  
    └─ Call AI Provider (Gemini/OpenAI/Groq)
    ↓
add_conversation(prompt, response)
    ├─ Save to data/conversation_history.json
    └─ Return response to user
```

## Next Steps

To enhance this feature further, consider:
- Adding database support (SQLite/PostgreSQL) for better scalability
- Adding user/session-based history (currently shared globally)
- Implementing conversation categorization/tagging by user
- Adding export functionality (CSV/JSON export of history)
- Creating a UI dashboard to visualize conversation patterns
- Adding conversation threading for multi-turn contexts
