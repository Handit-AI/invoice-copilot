# Invoice Copilot Backend

A sophisticated AI agent system that processes invoice documents and generates interactive business reports with real-time UI updates.

## 🚀 Features

- **Multi-Agent Architecture**: Intelligent decision-making with specialized action classes
- **Document Processing**: Process invoices with Chunkr AI and extract structured data
- **Real-Time UI Generation**: Create React components with charts and visualizations
- **Self-Improving AI**: Handit.ai integration for observability and automatic error correction
- **Conversational Interface**: Chat with your invoices and get instant responses
- **Professional Reports**: Generate interactive dashboards with Recharts

## 🏗️ Architecture

```
User Request → MainDecisionAgent → Action Classes → UI Updates
     ↓              ↓                ↓              ↓
  Chat Input → Decision Making → File Operations → React Components
```

### Core Components

- **MainDecisionAgent**: Analyzes requests and decides which actions to take
- **EditFileAction**: Creates React components with charts and visualizations
- **SimpleReportAction**: Analyzes data and provides text-based insights
- **OtherRequestAction**: Handles off-topic requests with polite redirection
- **CodingAgent**: Orchestrates the entire workflow
- **Handit.ai**: Provides observability and self-improvement capabilities

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Handit.ai API key
- Chunkr AI API key (optional)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Handit-AI/invoice-copilot.git
cd invoice-copilot/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment example
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

### 5. Configure API Keys

Edit the `.env` file and add your API keys:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
HANDIT_API_KEY=your_handit_api_key_here
CHUNKR_API_KEY=your_chunkr_api_key_here

# Optional Configuration
OPENAI_MODEL=gpt-4o-mini-2024-07-18
```

## 🔑 Getting API Keys

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Add it to your `.env` file

### Handit.ai API Key
1. Visit [Handit.ai](https://www.handit.ai/)
2. Create an account
3. Get your API key from the dashboard
4. Add it to your `.env` file

### Chunkr AI API Key (Optional)
1. Visit [Chunkr.ai](https://chunkr.ai/)
2. Create an account
3. Get your API key
4. Add it to your `.env` file

## 🚀 Running the Application

### Development Mode

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Start the FastAPI server
python main.py
```

The server will start on `http://localhost:8000`

### Production Mode

```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 API Endpoints

### Health Check
```bash
GET /health
```

### Document Processing
```bash
# Bulk process multiple files
POST /api/documents/bulk-process

# Process directory
POST /api/documents/process-directory
```

### Chat Interface
```bash
# Send message to AI agent
POST /api/chat/message
```

## 💬 Usage Examples

### 1. Process Invoice Files

```bash
# Upload invoice files for processing
curl -X POST "http://localhost:8000/api/documents/bulk-process" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@invoice1.pdf" \
  -F "files=@invoice2.pdf"
```

### 2. Chat with Your Invoices

```bash
# Ask questions about your invoice data
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a bar chart of monthly expenses",
    "workspace_dir": "frontend/src/components"
  }'
```

### 3. Get Data Insights

```bash
# Ask for specific data analysis
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my total revenue for this month?",
    "workspace_dir": "frontend/src/components"
  }'
```

## 🏗️ Project Structure

```
backend/
├── main.py                 # FastAPI application and endpoints
├── agent.py               # Multi-agent AI system
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── utils/
│   ├── call_llm.py      # LLM communication utility
│   ├── read_file.py     # File reading utility
│   ├── replace_file.py  # File editing utility
│   └── __init__.py
├── services/
│   └── handit_service.py # Handit.ai integration
├── processed/            # Processed invoice JSON files
└── logs/                # Application logs
```

## 🤖 AI Agent Workflow

1. **User Request**: Send a message to the AI agent
2. **Decision Making**: MainDecisionAgent analyzes the request
3. **Action Execution**: Specialized action classes perform tasks
4. **UI Updates**: React components are generated and updated
5. **Self-Improvement**: Handit.ai tracks performance and learns

### Action Types

- **EditFileAction**: Creates React components with charts
- **SimpleReportAction**: Analyzes data and provides insights
- **OtherRequestAction**: Handles off-topic requests
- **FormatResponseAction**: Generates final responses

## 🔍 Monitoring and Observability

### Handit.ai Integration

The system integrates with Handit.ai for:

- **Performance Monitoring**: Track response times and success rates
- **Error Detection**: Automatically detect and fix LLM mistakes
- **Self-Improvement**: Learn from failures and optimize prompts
- **Quality Evaluation**: Grade responses automatically

### Logging

- **Application Logs**: `logs/` directory
- **LLM Calls**: `logs/llm_calls_YYYYMMDD.log`
- **Agent Operations**: `coding_agent.log`

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Test Chat
```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me with my invoices?"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```bash
   # Check if API keys are set
   echo $OPENAI_API_KEY
   echo $HANDIT_API_KEY
   ```

2. **Virtual Environment**
   ```bash
   # Make sure virtual environment is activated
   which python
   # Should show: /path/to/project/.venv/bin/python
   ```

3. **Port Already in Use**
   ```bash
   # Kill process on port 8000
   lsof -ti:8000 | xargs kill -9
   ```

4. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Debug Mode

```bash
# Run with debug logging
DEBUG=True python main.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM communication |
| `HANDIT_API_KEY` | Yes | Handit.ai API key for observability |
| `CHUNKR_API_KEY` | No | Chunkr AI key for document processing |
| `OPENAI_MODEL` | No | LLM model (default: gpt-4o-mini-2024-07-18) |
| `LOG_DIR` | No | Log directory (default: logs) |

### Development Settings

```env
# Development mode
ENVIRONMENT=development
DEBUG=True

# Server settings
HOST=0.0.0.0
PORT=8000
```

## 📈 Performance

### Optimization Tips

1. **Caching**: Enable LLM response caching for repeated queries
2. **Batch Processing**: Process multiple files simultaneously
3. **Async Operations**: All file operations are asynchronous
4. **Error Handling**: Comprehensive error handling and recovery

### Monitoring

- **Response Times**: Tracked via Handit.ai
- **Success Rates**: Monitored automatically
- **Error Patterns**: Identified and fixed automatically
- **User Feedback**: Integrated for continuous improvement

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Handit-AI/invoice-copilot/issues)
- **Documentation**: [Project Wiki](https://github.com/Handit-AI/invoice-copilot/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/Handit-AI/invoice-copilot/discussions)

## 🙏 Acknowledgments

- **OpenAI**: For LLM capabilities
- **Handit.ai**: For AI observability, evaluation and self-improvement
- **Chunkr AI**: For document processing
- **FastAPI**: For the web framework
- **Recharts**: For data visualizations

---

**Built with ❤️ by the Invoice Copilot Team** 