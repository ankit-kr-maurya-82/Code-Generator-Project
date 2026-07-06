"""
Example script showing how to use the Conversation History Feature
Run this after starting the server: uvicorn main:app --reload
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def example_1_generate_with_history():
    """Example 1: Generate code (automatically stores in history)"""
    print_section("Example 1: Generate Code & Auto-Store")
    
    prompt = {
        "prompt": "Create a Python function to check if a number is prime"
    }
    
    print(f"Sending prompt: {prompt['prompt']}\n")
    
    response = requests.post(
        f"{BASE_URL}/generate",
        json=prompt
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Response received and stored in history!")
        print(f"\nResponse:\n{result['response'][:500]}...\n")
    else:
        print(f"❌ Error: {response.text}")

def example_2_view_history():
    """Example 2: View conversation history"""
    print_section("Example 2: View Recent Conversations")
    
    response = requests.get(f"{BASE_URL}/history?limit=5")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} recent conversation(s):\n")
        
        for i, conv in enumerate(data['conversations'], 1):
            print(f"Conversation {i}:")
            print(f"  📝 User: {conv['user_prompt'][:80]}...")
            print(f"  🤖 AI: {conv['ai_response'][:80]}...")
            print(f"  ⏰ Time: {conv['timestamp']}")
            print(f"  🏷️  Tags: {', '.join(conv['tags'])}\n")
    else:
        print(f"❌ Error: {response.text}")

def example_3_get_statistics():
    """Example 3: Get conversation statistics"""
    print_section("Example 3: Conversation Statistics")
    
    response = requests.get(f"{BASE_URL}/history/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Total Conversations: {stats['total_conversations']}\n")
        
        if stats['top_topics']:
            print("Top Topics Discussed:")
            for topic, count in sorted(stats['top_topics'].items(), key=lambda x: x[1], reverse=True):
                print(f"  • {topic}: {count} times")
        else:
            print("No topics yet - start asking questions!")
            
        if stats['first_conversation']:
            print(f"\nFirst conversation: {stats['first_conversation']}")
            print(f"Last conversation: {stats['last_conversation']}")
    else:
        print(f"❌ Error: {response.text}")

def example_4_search_history():
    """Example 4: Search conversation history"""
    print_section("Example 4: Search Conversations")
    
    keyword = "function"
    print(f"Searching for conversations about: '{keyword}'\n")
    
    response = requests.get(
        f"{BASE_URL}/history/search",
        params={"keyword": keyword}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} conversation(s) with '{keyword}':\n")
        
        for i, conv in enumerate(data['conversations'], 1):
            print(f"Result {i}:")
            print(f"  📝 User: {conv['user_prompt'][:100]}...")
            print(f"  🤖 AI: {conv['ai_response'][:100]}...")
            print(f"  ⏰ Time: {conv['timestamp']}\n")
    else:
        print(f"❌ Error: {response.text}")

def example_5_related_questions():
    """Example 5: Show how related questions use history"""
    print_section("Example 5: Related Questions (Using History)")
    
    questions = [
        "Create a function to sort a list in Python",
        "How do I sort a dictionary instead?",
        "What about sorting a list in reverse order?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question}")
        print("→ System automatically finds related conversations")
        print("→ AI generates response with historical context")
        print("→ Response is consistent with previous answers\n")
        
        # Make the actual API call
        response = requests.post(
            f"{BASE_URL}/generate",
            json={"prompt": question}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response stored in history (will be used for next question)")
        else:
            print(f"❌ Error: {response.text}")

def example_6_conversation_flow():
    """Example 6: Shows a realistic conversation flow"""
    print_section("Example 6: Realistic Conversation Flow")
    
    conversation = [
        "Show me how to read a file in Python",
        "How do I write to that file?",
        "What about reading/writing JSON files?",
        "How would I handle file errors?"
    ]
    
    print("This shows a realistic conversation where each answer")
    print("builds on previous ones through history context:\n")
    
    for i, prompt in enumerate(conversation, 1):
        print(f"Q{i}: {prompt}")
        
        # Show what the system does
        if i == 1:
            print("    → First question, no history to reference")
        else:
            print(f"    → System finds previous {i-1} conversation(s)")
            print(f"    → Passes context to AI for consistency")
        
        print("    → Response stored in history\n")

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("  CONVERSATION HISTORY FEATURE - EXAMPLES")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  Command: uvicorn main:app --reload\n")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/history", timeout=2)
        print("✅ Server is running and responding!\n")
    except:
        print("❌ Server is not responding. Start it with:")
        print("   uvicorn main:app --reload\n")
        return
    
    # Run examples
    example_1_generate_with_history()
    example_2_view_history()
    example_3_get_statistics()
    example_4_search_history()
    example_5_related_questions()
    example_6_conversation_flow()
    
    print("\n" + "="*60)
    print("  ALL EXAMPLES COMPLETED!")
    print("="*60)
    print("\nKey Points:")
    print("✓ Every generate request stores the conversation")
    print("✓ AI automatically uses history context")
    print("✓ Responses become more consistent over time")
    print("✓ Use /history endpoints to view and analyze")
    print("✓ Topics are automatically extracted and tracked\n")

if __name__ == "__main__":
    main()
