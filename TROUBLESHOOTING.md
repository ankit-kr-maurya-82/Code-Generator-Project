# 🔧 Troubleshooting Guide

## Common Issues & Solutions

---

## ❌ Issue 1: Server won't start

### Error: `ImportError: No module named 'models.conversation'`

**Solution:**
```bash
# Run from project root directory
cd "e:\Code generator Project"

# Restart the server
uvicorn main:app --reload
```

---

## ❌ Issue 2: `data/conversation_history.json` not found

### Error: `FileNotFoundError: No such file or directory`

**Solution:**
The file is created automatically on first request. Just make your first request:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

---

## ❌ Issue 3: History endpoints returning 404

### Error: `{"detail":"Not found"}`

**Solution:**
Make sure you're using the correct routes:
```bash
# ✅ CORRECT
GET http://localhost:8000/history
GET http://localhost:8000/history/stats
GET http://localhost:8000/history/search?keyword=test
POST http://localhost:8000/history/clear

# ❌ INCORRECT (won't work)
GET http://localhost:8000/get-history
GET http://localhost:8000/search
```

---

## ❌ Issue 4: History not being stored

### Problem: No data in `/history`

**Debugging Steps:**

1. **Check that generate endpoint returns 200:**
   ```bash
   curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Test question"}' -w "\nStatus: %{http_code}\n"
   ```

2. **Check if history file exists:**
   ```bash
   # Windows PowerShell
   Test-Path "data/conversation_history.json"
   
   # Or just look in the data folder
   dir data/
   ```

3. **Check history file content:**
   ```bash
   cat data/conversation_history.json
   ```

4. **If empty, try a fresh generate:**
   ```bash
   curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "How do I print in Python?"}'
   ```

---

## ❌ Issue 5: Search not finding conversations

### Problem: `GET /history/search?keyword=python` returns empty

**Solution:**

1. **Make sure history has conversations first:**
   ```bash
   # Generate some conversations
   curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Write Python code to reverse a string"}'
   ```

2. **Use exact keyword from prompts:**
   ```bash
   # If you asked about "python", search for "python"
   GET http://localhost:8000/history/search?keyword=python
   
   # Not "py" or "Python" (case-insensitive but needs to exist)
   ```

3. **Check what topics exist:**
   ```bash
   # Get statistics to see top keywords
   curl http://localhost:8000/history/stats
   ```

---

## ❌ Issue 6: AI responses not using history

### Problem: AI responses don't reference previous conversations

**This is actually expected behavior if:**

1. **History is empty** - First few requests won't have history to use
2. **No relevant conversations** - If questions are completely different
3. **Keywords don't match** - If new question has no common keywords

**To verify history is being used:**

1. Ask 2-3 related questions:
   ```bash
   # Q1: About sorting lists
   curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "How do I sort a list in Python?"}'
   
   # Q2: About sorting dicts (should reference lists)
   curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "How about sorting a dictionary?"}'
   ```

2. Check if context appears in response

---

## ❌ Issue 7: Permission denied when saving history

### Error: `PermissionError: [Errno 13] Permission denied`

**Solution:**

1. **Check folder permissions:**
   ```bash
   # Windows: Run cmd as Administrator
   # Then run the server again
   ```

2. **Create data folder manually:**
   ```bash
   # PowerShell
   New-Item -ItemType Directory -Path "data" -Force
   ```

3. **Check file permissions:**
   ```bash
   # Windows
   icacls "data" /grant %username%:F
   ```

---

## ❌ Issue 8: `ModuleNotFoundError` for services

### Error: `ModuleNotFoundError: No module named 'services.history_service'`

**Solution:**

1. **Make sure files exist:**
   ```bash
   # Check these files exist:
   ls -la services/history_service.py
   ls -la services/history_analysis.py
   ls -la models/conversation.py
   ```

2. **Check __init__.py files:**
   ```bash
   # Make sure these exist:
   services/__init__.py
   models/__init__.py
   ```

3. **Restart server:**
   ```bash
   # Stop current server (Ctrl+C)
   # Then restart
   uvicorn main:app --reload
   ```

---

## ❌ Issue 9: JSON parsing errors

### Error: `json.decoder.JSONDecodeError`

**Solution:**

1. **Backup and clear corrupted history:**
   ```bash
   # Backup
   cp data/conversation_history.json data/conversation_history.backup.json
   
   # Clear (this will reset it)
   curl -X POST "http://localhost:8000/history/clear"
   ```

2. **Or manually fix the file:**
   ```bash
   # Make sure it has valid structure:
   {
     "conversations": [],
     "total_count": 0
   }
   ```

---

## ❌ Issue 10: Large history file slowing down system

### Problem: System feels slow after many conversations

**Solution:**

1. **Check file size:**
   ```bash
   # Windows PowerShell
   (Get-Item "data/conversation_history.json").Length / 1MB
   ```

2. **If > 10MB, clear and restart:**
   ```bash
   curl -X POST "http://localhost:8000/history/clear"
   ```

3. **Or manually trim old entries:**
   - Edit `data/conversation_history.json`
   - Keep only recent conversations
   - Make sure JSON is valid

---

## 🔍 Debugging Commands

### Check Server Status
```bash
# Test if server responds
curl "http://localhost:8000/"

# Get error details
curl -v "http://localhost:8000/history"
```

### View Full History
```bash
# Windows PowerShell
Get-Content "data/conversation_history.json" -Raw | ConvertFrom-Json | ConvertTo-Json
```

### Check Logs
```bash
# Look at terminal where uvicorn is running
# It shows errors like:
# - ImportError
# - SyntaxError  
# - Connection errors
```

### Manual History Testing
```bash
# Create new conversation
$body = @{"prompt"="Test"} | ConvertTo-Json
curl -X POST "http://localhost:8000/generate" `
  -H "Content-Type: application/json" `
  -Body $body

# Check if stored
curl "http://localhost:8000/history"
```

---

## ✅ Verification Checklist

When something doesn't work, check:

- [ ] Server is running (`uvicorn main:app --reload`)
- [ ] Using correct endpoint URLs
- [ ] JSON syntax is valid
- [ ] `data/` directory exists
- [ ] Python imports are working (check logs)
- [ ] History file exists and is valid JSON
- [ ] Generated at least 1 conversation

---

## 📞 Still Not Working?

### Check These Files:

1. **Error in models/conversation.py?**
   ```bash
   python -c "from models.conversation import Conversation; print('OK')"
   ```

2. **Error in history_service.py?**
   ```bash
   python -c "from services.history_service import load_history; print('OK')"
   ```

3. **Error in routes/generate.py?**
   ```bash
   python -c "from routes.generate import router; print('OK')"
   ```

### Check Syntax
```bash
# Validate all Python files
python -m py_compile models/conversation.py
python -m py_compile services/history_service.py
python -m py_compile services/history_analysis.py
```

### Reset Everything
```bash
# Remove history
Remove-Item "data/conversation_history.json"

# Restart server
# (Stop with Ctrl+C and run again)
uvicorn main:app --reload

# Make a test request
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

---

## 📊 Performance Tips

If history is slow:

1. **Limit search results:**
   ```bash
   # Instead of searching all
   # Search with timeouts
   ```

2. **Archive old history:**
   ```bash
   # Periodically backup and clear
   cp data/conversation_history.json data/history_backup_$(date).json
   curl -X POST "http://localhost:8000/history/clear"
   ```

3. **Monitor file size:**
   ```bash
   # Check size monthly
   (Get-Item "data/conversation_history.json").Length / 1MB
   ```

---

## 💡 Quick Recovery

If everything breaks:

```bash
# 1. Stop server
# (Press Ctrl+C)

# 2. Remove history file
Remove-Item "data/conversation_history.json"

# 3. Restart
uvicorn main:app --reload

# 4. Make first request
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

---

**Most issues are resolved by:**
1. Restarting the server
2. Checking file paths
3. Clearing and recreating history

**Happy coding! 🚀**
