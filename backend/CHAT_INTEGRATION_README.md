# 🤖 Chat Integration with Coding Agent

This integration connects the frontend chat interface with the backend coding agent, allowing users to interact with their workspace files through natural language.

## 🔗 Architecture

```
Frontend Chat → API Call → Backend Endpoint → Coding Agent → File Operations → Response
```

### Components:

1. **Frontend Chat** (`ChatArea.tsx`): User interface for sending messages
2. **Chat API** (`chatApi.ts`): Service for communicating with backend
3. **Backend Endpoint** (`/api/chat/message`): Processes chat messages
4. **Coding Agent** (`agent.py`): Executes file operations and code analysis

## 🚀 Features

### ✅ Available Commands:

- **📂 File Operations**: List, read, create, delete files
- **🔍 Search**: Find patterns, content, and code structures
- **✏️ Edit**: Modify files with natural language instructions
- **🧪 Semantic Search**: Find similar content using AI embeddings
- **🔧 Code Analysis**: Understand and analyze code structure

### 💬 Example Queries:

```
"List all files in the workspace"
"Read the DynamicWorkspace.tsx file"
"Search for all components that use useState"
"Edit DynamicWorkspace.tsx to add a loading spinner"
"Create a new button component"
"Find documents about invoices using semantic search"
```

## 🛠️ Setup & Usage

### Prerequisites:
```bash
# Backend dependencies
pip install fastapi uvicorn pyyaml

# Optional: For semantic search
pip install pinecone-client openai

# Environment variables
export PINECONE_API_KEY="your-key"
export PINECONE_INDEX_NAME="your-index"
export OPENAI_API_KEY="your-key"
```

### Start the Backend:
```bash
cd backend
python main.py
```

### Start the Frontend:
```bash
cd frontend
npm run dev
```

### Test the Integration:
```bash
cd backend
python test_chat_integration.py

# Or interactive mode:
python test_chat_integration.py --interactive

# Or single message:
python test_chat_integration.py --message "List files in workspace"
```

## 📡 API Reference

### POST `/api/chat/message`

**Request:**
```json
{
  "message": "Read the DynamicWorkspace.tsx file",
  "workspace_dir": "frontend/src/components/workspace",
  "max_iterations": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Read the DynamicWorkspace.tsx file",
  "response": "Here's the content of DynamicWorkspace.tsx...",
  "workspace_dir": "frontend/src/components/workspace",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "File not found",
  "response": "I couldn't find the file you requested.",
  "workspace_dir": "frontend/src/components/workspace",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🎯 Agent Capabilities

### 1. **File Operations**
```python
# List directory contents
"List all files in the workspace"

# Read specific files  
"Read the DynamicWorkspace.tsx file"
"Show me the content of ExpensesReport.tsx"

# Edit files
"Add a comment to the top of DynamicWorkspace.tsx"
"Edit the workspace component to add a loading state"
```

### 2. **Search Operations**
```python
# Text search
"Search for 'useState' in all files"
"Find all components that import React"

# Semantic search (requires Pinecone)
"Find documents about payment processing"
"Search for content similar to 'invoice data analysis'"
```

### 3. **Code Analysis**
```python
# Component structure
"Analyze the DynamicWorkspace component structure"
"Show me all the props used in ExpensesReport"

# Dependencies
"What components does WorkspaceArea depend on?"
"List all imports in the workspace files"
```

## 🔧 Configuration

### Working Directory:
The agent operates in the specified workspace directory:
- Default: `frontend/src/components/workspace`
- Configurable via API request
- Relative to the backend process location

### Agent Settings:
- **Max Iterations**: Prevents infinite loops (default: 10)
- **Tool Selection**: Automatic based on user intent
- **Error Handling**: Graceful fallbacks and user-friendly messages

## 🚨 Error Handling

### Common Issues:

1. **Backend Not Running**
   ```
   Error: Cannot connect to backend
   Solution: Start backend with `python main.py`
   ```

2. **Agent Import Error**
   ```
   Error: Coding agent not available
   Solution: Ensure agent.py and utils are in backend directory
   ```

3. **File Not Found**
   ```
   Error: File does not exist
   Solution: Check file paths and workspace directory
   ```

4. **Permission Denied**
   ```
   Error: Cannot write to file
   Solution: Check file permissions and directory access
   ```

## 📊 Logging

The integration provides detailed logging:

```bash
# Backend logs
INFO: 💬 Processing chat message: List files in workspace
INFO: 📁 Working directory: frontend/src/components/workspace  
INFO: ✅ Chat processing completed

# Frontend logs (browser console)
📤 Sending chat message to backend: "List files"
✅ Received chat response: {...}
```

## 🔒 Security

### CORS Configuration:
```python
allowed_origins = [
    "http://localhost:3000",  # Next.js dev
    "http://localhost:3001",  # Alternative port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
]
```

### File Access:
- Limited to specified workspace directory
- No access to system files or parent directories
- Read/write permissions based on file system

## 🧪 Testing

### Manual Testing:
1. Start backend and frontend
2. Open chat interface
3. Try example queries
4. Verify file operations work correctly

### Automated Testing:
```bash
# Run test suite
python test_chat_integration.py

# Test specific functionality
python test_chat_integration.py --message "List workspace files"
```

### Integration Tests:
- ✅ Health check endpoint
- ✅ File listing operations  
- ✅ File reading operations
- ✅ Search functionality
- ✅ Edit operations
- ✅ Error handling

## 💡 Usage Tips

### Effective Prompts:
- Be specific about file names and locations
- Use clear action words (read, edit, search, create)
- Provide context for edits and modifications
- Ask for explanations when analyzing code

### Best Practices:
- Start with file listing to understand structure
- Read files before editing them
- Use semantic search for content discovery
- Combine operations in natural language

### Example Workflows:

1. **Explore Codebase:**
   ```
   "List all files in workspace"
   "Read DynamicWorkspace.tsx"
   "Search for useState hooks"
   ```

2. **Make Changes:**
   ```
   "Read ExpensesReport.tsx"
   "Edit it to add error handling"
   "Search for similar error patterns"
   ```

3. **Create Components:**
   ```
   "Create a new LoadingSpinner component"
   "Add it to DynamicWorkspace.tsx"
   "Update the imports"
   ```

This integration makes code exploration and modification as easy as having a conversation! 🎉