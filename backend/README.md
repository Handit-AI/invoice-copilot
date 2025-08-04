# Simple FastAPI Backend

A basic FastAPI backend with virtual environment setup and a health endpoint.

## Features

- 🏥 Health check endpoint
- 🚀 Virtual environment setup
- 📝 Simple logging
- 🌐 Auto-generated API documentation

## Quick Setup

### 1. Setup (creates venv and installs dependencies)
```bash
cd backend
python3 setup.py
```

### 2. Run the server
```bash
python3 run.py
```

## Manual Setup

### 1. Create virtual environment
```bash
python3 -m venv venv
```

### 2. Activate virtual environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
python main.py
```

## API Endpoints

### Health Check
- **GET** `/health`
- Returns server status and timestamp

Example response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-03T17:00:00.000000",
  "version": "1.0.0"
}
```

## API Documentation

Once the server is running:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health endpoint**: http://localhost:8000/health

## Testing

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

## Project Structure

```
backend/
├── main.py          # FastAPI application
├── requirements.txt # Dependencies
├── setup.py         # Setup script (creates venv)
├── run.py           # Run script (uses venv)
├── README.md        # This file
└── venv/            # Virtual environment (created by setup.py)
```