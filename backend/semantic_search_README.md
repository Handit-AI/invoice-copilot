# 🔍 Semantic Search Tool for Pinecone

This tool provides semantic search capabilities using Pinecone's integrated embeddings for the coding agent system.

## ✨ Features

- **Basic Semantic Search**: Find semantically similar content using natural language queries
- **Category Filtering**: Search within specific categories (e.g., "finance", "history")
- **File-Specific Search**: Search within specific documents/files
- **Agent Integration**: Works seamlessly with the coding agent workflow
- **Formatted Results**: Human-readable search results with scores and metadata

## 🚀 Quick Start

### Environment Setup

```bash
# Set required environment variables
export PINECONE_API_KEY="your-pinecone-api-key"
export PINECONE_INDEX_NAME="your-index-name"  # Default: "invoice-copilot"
```

### Using with Coding Agent

```python
from agent import CodingAgent

# Initialize agent
agent = CodingAgent()

# Semantic search via natural language
response = agent.process_request("Find documents about invoice processing and payments")
print(response)
```

### Direct Function Calls

```python
from utils.semantic_search import semantic_search, format_search_results

# Basic search
success, results = semantic_search(
    query="Famous historical structures and monuments",
    namespace="example-namespace",
    top_k=5
)

if success:
    formatted = format_search_results(results)
    print(formatted)
```

## 🛠️ Available Functions

### `semantic_search(query, namespace, top_k, ...)`
Basic semantic search using Pinecone's integrated embeddings.

**Parameters:**
- `query` (str): Text query to search for
- `namespace` (str, optional): Pinecone namespace (default: "example-namespace")
- `top_k` (int, optional): Number of results to return (default: 10, max: 10000)
- `index_name` (str, optional): Index name (uses env var if not provided)
- `api_key` (str, optional): API key (uses env var if not provided)

**Returns:**
- `(success: bool, results: List[Dict])`

### `search_by_category(query, category, ...)`
Search within a specific category using metadata filtering.

**Example:**
```python
success, results = search_by_category(
    query="payment processing",
    category="finance",
    top_k=5
)
```

### `search_by_filename(query, filename, ...)`
Search within a specific file.

**Example:**
```python
success, results = search_by_filename(
    query="invoice total",
    filename="invoice_001.pdf",
    top_k=3
)
```

### `format_search_results(results, max_text_length)`
Format search results into human-readable text.

## 🎯 Agent Tool Usage

When using the coding agent, you can trigger semantic search with natural language:

### Example Queries:

```yaml
# Basic search
tool: semantic_search
reason: I need to find documents about invoices and payments
params:
  query: "invoice payment processing"
  namespace: "example-namespace"
  top_k: 5

# Category-filtered search
tool: semantic_search
reason: I need to find historical documents about monuments
params:
  query: "monuments and structures"
  namespace: "example-namespace"
  top_k: 3
  category_filter: "history"

# File-specific search
tool: semantic_search
reason: I need to find payment information in a specific invoice
params:
  query: "payment due date"
  filename_filter: "invoice_001.pdf"
  top_k: 5
```

## 📊 Response Format

### Successful Response:
```python
{
    "success": True,
    "results": [
        {
            "id": "rec1", 
            "score": 0.85,
            "metadata": {
                "category": "finance",
                "content": "Invoice processing workflow...",
                "original_filename": "invoice_001.pdf"
            }
        }
    ],
    "formatted_results": "Found 1 results:\n1. ID: rec1 | Score: 0.850...",
    "query": "invoice processing",
    "namespace": "example-namespace", 
    "total_results": 1
}
```

### Error Response:
```python
{
    "success": False,
    "results": [],
    "formatted_results": "",
    "query": "...",
    "namespace": "...",
    "total_results": 0
}
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
cd backend
python test_semantic_search.py
```

The test script will:
- Test agent integration with various query types
- Test direct function calls
- Show usage examples
- Check environment configuration

## 📋 Requirements

- `pinecone-client>=3.0.0`
- `pyyaml`
- Environment variables: `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`

## 🔧 Configuration

### Default Settings:
- **Default Namespace**: "example-namespace"
- **Default Index Name**: "invoice-copilot" 
- **Default Top K**: 10
- **Max Results**: 10,000 (Pinecone limit)

### Metadata Fields:
The tool expects these common metadata fields:
- `category`: Document category
- `content` or `chunk_text`: Text content
- `original_filename`: Source file name

## 🚨 Troubleshooting

### Common Issues:

1. **"Pinecone API key not provided"**
   - Set `PINECONE_API_KEY` environment variable

2. **"No results found"**
   - Check if your index has data
   - Verify namespace name
   - Try different query terms

3. **Import errors**
   - Install required dependencies: `pip install pinecone-client pyyaml`

4. **Search fails**
   - Ensure your Pinecone index is configured for integrated embeddings
   - Check index name and namespace

## 💡 Tips

- Use natural language queries for best results
- Try different query phrasings if initial results aren't relevant
- Use category filters to narrow down search scope
- Experiment with different `top_k` values based on your needs
- Check metadata fields to understand available filtering options

## 🔗 Integration with Main Agent

The semantic search tool is fully integrated with the main coding agent system:

1. **Automatic Tool Selection**: The agent will choose semantic search when queries involve finding similar content
2. **History Tracking**: All searches are logged in the agent's history
3. **Error Handling**: Graceful error handling and reporting
4. **Response Formatting**: Results are formatted for easy reading

This makes it easy to combine semantic search with other tools like file reading and editing in complex workflows.