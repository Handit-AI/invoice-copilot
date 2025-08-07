#!/usr/bin/env python3
"""
Invoice Copilot Backend - FastAPI Application

This module provides a FastAPI backend service for the Invoice Copilot application.
It includes endpoints for document processing using Chunkr AI, chat functionality
with a coding agent, and health monitoring.

Key Features:
- Document processing with Chunkr AI for invoice analysis
- Bulk file upload and processing
- Directory-based document processing
- Chat interface with AI coding agent
- Health monitoring and status endpoints
- CORS configuration for frontend integration

Dependencies:
- FastAPI: Web framework
- Chunkr AI: Document processing
- Handit.ai: AI observability and monitoring
- Python 3.8+

Author: coderTtxi12
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import asyncio
from chunkr_ai import Chunkr
import os
from pathlib import Path
from typing import List, Optional
import tempfile
import json
import uuid
from dotenv import load_dotenv

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Configure logging with timestamp and level information
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# AI SERVICE INITIALIZATION
# =============================================================================

# Initialize Chunkr AI service for document processing
chunkr = Chunkr()

# =============================================================================
# FASTAPI APPLICATION SETUP
# =============================================================================

# Create FastAPI application instance with metadata
app = FastAPI(
    title="Invoice Copilot Backend",
    description="FastAPI backend for Invoice Copilot with document processing and AI chat capabilities",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc"  # ReDoc documentation
)

# =============================================================================
# CORS CONFIGURATION
# =============================================================================

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
# This allows the frontend to communicate with the backend
allowed_origins = [
    "http://localhost:3000",    # Next.js development server
    "http://localhost:3001",    # Alternative Next.js port
    "http://127.0.0.1:3000",   # Localhost alternative
    "http://127.0.0.1:3001",   # Localhost alternative
    "http://localhost:8000",    # FastAPI development server
    "http://127.0.0.1:8000",   # FastAPI alternative
    "http://localhost:8080",    # Alternative development port
    "http://127.0.0.1:8080"    # Alternative development port
]

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    
    Returns:
        dict: Service status information including:
            - status: Always "healthy"
            - timestamp: Current ISO timestamp
            - version: API version number
    
    Example Response:
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00.123456",
            "version": "1.0.0"
        }
    """
    logger.info("🏥 Health check requested")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# =============================================================================
# DOCUMENT PROCESSING FUNCTIONS
# =============================================================================

async def process_file_with_chunkr(chunkr, file_path: Path, output_dir: Path):
    """
    Process a single file using Chunkr AI service.
    
    This function uploads a file to Chunkr AI for processing and saves the results
    to a JSON file in the specified output directory.
    
    Args:
        chunkr: Chunkr AI service instance
        file_path (Path): Path to the file to be processed
        output_dir (Path): Directory where processed results will be saved
    
    Returns:
        dict: Processing result containing:
            - file_name: Name of the processed file
            - status: "success", "failed", or "error"
            - output_file: Path to output file (if successful)
            - error: Error message (if failed or error)
    
    Raises:
        Exception: Any exception during processing is caught and returned as error
    
    Example:
        result = await process_file_with_chunkr(chunkr, Path("invoice.pdf"), Path("output"))
        # Returns: {"file_name": "invoice.pdf", "status": "success", "output_file": "output/invoice.pdf.json"}
    """
    try:
        logger.info(f"📄 Processing file: {file_path.name}")
        
        # Upload file to Chunkr AI for processing
        result = await chunkr.upload(file_path)
        
        # Check if upload was successful
        if result.status == "Failed":
            logger.error(f"❌ Failed to process file {file_path.name}: {result.message}")
            return {
                "file_name": file_path.name,
                "status": "failed",
                "error": result.message
            }
        
        # Save processing result to output directory as JSON
        output_file_path = output_dir / f"{file_path.name}.json"
        result.json(output_file_path)
        
        logger.info(f"✅ Successfully processed: {file_path.name}")
        return {
            "file_name": file_path.name,
            "status": "success",
            "output_file": str(output_file_path)
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing file {file_path.name}: {str(e)}")
        return {
            "file_name": file_path.name,
            "status": "error",
            "error": str(e)
        }

# =============================================================================
# BULK DOCUMENT PROCESSING ENDPOINT
# =============================================================================

@app.post("/api/documents/bulk-process")
async def bulk_document_processing(
    files: List[UploadFile] = File(...),
    output_dir: Optional[str] = None
):
    """
    Bulk document processing endpoint using Chunkr AI.
    
    This endpoint accepts multiple files and processes them concurrently using
    Chunkr AI. Files are temporarily saved, processed in parallel, and results
    are saved to the specified output directory.
    
    Args:
        files (List[UploadFile]): List of files to process (required)
        output_dir (Optional[str]): Output directory path (defaults to 'processed/')
    
    Returns:
        dict: Processing summary containing:
            - message: Success message
            - total_files: Number of files processed
            - successful: Number of successfully processed files
            - failed: Number of failed files
            - output_directory: Path to output directory
            - timestamp: Processing timestamp
            - results: Detailed results for each file
    
    Raises:
        HTTPException: If processing fails with 500 status code
    
    Example Request:
        POST /api/documents/bulk-process
        Content-Type: multipart/form-data
        files: [file1.pdf, file2.pdf, file3.pdf]
        output_dir: "my_output"
    
    Example Response:
        {
            "message": "Bulk document processing completed",
            "total_files": 3,
            "successful": 2,
            "failed": 1,
            "output_directory": "my_output",
            "timestamp": "2024-01-15T10:30:00.123456",
            "results": [...]
        }
    """
    logger.info(f"📄 Bulk document processing requested - {len(files)} files")
    
    try:
        # Set default output directory if not provided
        if output_dir is None:
            output_dir = "processed"
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        # Create temporary directory for uploaded files
        # This ensures files are cleaned up after processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded files to temporary directory
            saved_files = []
            for file in files:
                if file.filename:
                    file_path = temp_path / file.filename
                    content = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(content)
                    saved_files.append(file_path)
            
            logger.info(f"💾 Saved {len(saved_files)} files to temporary directory")
            
            # Process files concurrently using asyncio
            # This improves performance for multiple files
            tasks = []
            for file_path in saved_files:
                task = asyncio.create_task(
                    process_file_with_chunkr(chunkr, file_path, output_path)
                )
                tasks.append(task)
            
            # Wait for all files to complete processing
            results = await asyncio.gather(*tasks)
            
            # Count successful and failed processing attempts
            successful = [r for r in results if r["status"] == "success"]
            failed = [r for r in results if r["status"] in ["failed", "error"]]
            
            logger.info(f"✅ Completed processing: {len(successful)} successful, {len(failed)} failed")
            
            return {
                "message": "Bulk document processing completed",
                "total_files": len(files),
                "successful": len(successful),
                "failed": len(failed),
                "output_directory": str(output_path),
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
            
    except Exception as e:
        logger.error(f"❌ Error in bulk processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

# =============================================================================
# DIRECTORY PROCESSING ENDPOINT
# =============================================================================

@app.post("/api/documents/process-directory")
async def process_directory_endpoint(
    input_dir: str,
    output_dir: Optional[str] = None
):
    """
    Process all documents in a directory using Chunkr AI.
    
    This endpoint processes all files in a specified directory. It scans the
    directory for files and processes them concurrently using Chunkr AI.
    
    Args:
        input_dir (str): Directory path containing files to process
        output_dir (Optional[str]): Output directory path (defaults to 'processed/')
    
    Returns:
        dict: Processing summary containing:
            - message: Success message
            - input_directory: Path to input directory
            - output_directory: Path to output directory
            - total_files: Number of files found
            - successful: Number of successfully processed files
            - failed: Number of failed files
            - timestamp: Processing timestamp
            - results: Detailed results for each file
    
    Raises:
        HTTPException: 
            - 400: If input directory doesn't exist
            - 500: If processing fails
    
    Example Request:
        POST /api/documents/process-directory
        {
            "input_dir": "/path/to/documents",
            "output_dir": "/path/to/output"
        }
    
    Example Response:
        {
            "message": "Directory processing completed",
            "input_directory": "/path/to/documents",
            "output_directory": "/path/to/output",
            "total_files": 5,
            "successful": 4,
            "failed": 1,
            "timestamp": "2024-01-15T10:30:00.123456",
            "results": [...]
        }
    """
    logger.info(f"📁 Directory processing requested: {input_dir}")
    
    try:
        # Validate input directory exists
        input_path = Path(input_dir)
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Input directory does not exist: {input_dir}")
        
        # Set default output directory if not provided
        if output_dir is None:
            output_dir = "processed"
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        # Get all files in directory (any file with an extension)
        files = list(input_path.glob('*.*'))
        logger.info(f"📄 Found {len(files)} files to process")
        
        # Return early if no files found
        if not files:
            return {
                "message": "No files found in directory",
                "input_directory": str(input_path),
                "total_files": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Process files concurrently using asyncio
        tasks = []
        for file_path in files:
            task = asyncio.create_task(
                process_file_with_chunkr(chunkr, file_path, output_path)
            )
            tasks.append(task)
        
        # Wait for all files to complete processing
        results = await asyncio.gather(*tasks)
        
        # Count successful and failed processing attempts
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] in ["failed", "error"]]
        
        logger.info(f"✅ Directory processing completed: {len(successful)} successful, {len(failed)} failed")
        
        return {
            "message": "Directory processing completed",
            "input_directory": str(input_path),
            "output_directory": str(output_path),
            "total_files": len(files),
            "successful": len(successful),
            "failed": len(failed),
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for invalid directory)
        raise
    except Exception as e:
        logger.error(f"❌ Error in directory processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing directory: {str(e)}")

# =============================================================================
# CODING AGENT INTEGRATION
# =============================================================================

# Import the coding agent with error handling
try:
    from agent import CodingAgent
    agent_available = True
    logger.info("✅ Coding agent imported successfully")
except ImportError as e:
    agent_available = False
    logger.warning(f"⚠️ Coding agent not available: {str(e)}")

# =============================================================================
# CHAT ENDPOINT
# =============================================================================

@app.post("/api/chat/message")
async def process_chat_message(message: dict):
    """
    Process chat messages using the coding agent.
    
    This endpoint handles chat messages and uses the coding agent to process
    user requests. The agent can modify code files based on user instructions.
    
    Args:
        message (dict): Dictionary containing:
            - message (str): User's message/request (required)
            - workspace_dir (str): Working directory for the agent (optional)
            - max_iterations (int): Maximum iterations for agent processing (optional)
    
    Returns:
        dict: Processing result containing:
            - success (bool): Whether processing was successful
            - message (str): Original user message
            - response (str): Agent's response
            - workspace_dir (str): Working directory used
            - timestamp (str): Processing timestamp
            - error (str): Error message (if failed)
    
    Example Request:
        POST /api/chat/message
        {
            "message": "Add a new button component",
            "workspace_dir": "frontend/src/components",
            "max_iterations": 5
        }
    
    Example Response:
        {
            "success": true,
            "message": "Add a new line graph",
            "response": "I've created a new line graph component...",
            "workspace_dir": "frontend/src/components/workspace",
            "timestamp": "2024-01-15T10:30:00.123456"
        }
    """
    try:
        # Extract parameters from the message
        user_message = message.get("message", "")
        workspace_dir = message.get("workspace_dir", "frontend/src/components/workspace/DynamicWorkspace.tsx")
        max_iterations = message.get("max_iterations", 3)
        
        # Validate required parameters
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Check if coding agent is available
        if not agent_available:
            return {
                "success": False,
                "error": "Coding agent not available",
                "response": "I'm sorry, but the coding agent is not currently available. Please check the backend configuration."
            }
        
        logger.info(f"💬 Processing chat message: {user_message}")
        logger.info(f"📁 Working directory: {workspace_dir}")
        
        # Initialize the coding agent with the specified workspace directory
        agent = CodingAgent(working_dir=workspace_dir)
        
        # Process the user's message with the specified maximum iterations
        response = agent.process_request(user_message, max_iterations=max_iterations)
        
        logger.info(f"✅ Chat processing completed")
        
        return {
            "success": True,
            "message": user_message,
            "response": response,
            "workspace_dir": workspace_dir,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing chat message: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "response": f"I encountered an error while processing your request: {str(e)}"
        }

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def check_handit_configuration():
    """
    Check if Handit.ai is properly configured.
    
    This function validates that the Handit.ai API key is set in the environment
    variables. It provides helpful error messages and setup instructions if the
    configuration is missing.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    
    Note:
        This function prints configuration status and setup instructions to stdout.
        It's designed to be called during application startup.
    """
    handit_api_key = os.getenv("HANDIT_API_KEY")
    
    if not handit_api_key:
        print("❌ ERROR: Handit.ai API key is required to run this project!")
        print("")
        print("📋 To get started:")
        print("1. Visit https://www.handit.ai/ to create an account")
        print("2. Get your API key from the dashboard")
        print("3. Add HANDIT_API_KEY=your_api_key_here to your .env file")
        print("")
        print("🔧 Example .env file:")
        print("HANDIT_API_KEY=your_handit_api_key_here")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("")
        print("💡 Handit.ai provides:")
        print("   • AI Observability - Monitor your AI agents")
        print("   • Quality Evaluation - Automatically grade responses")
        print("   • Self-Improving AI - Auto-optimize prompts")
        print("")
        return False
    
    print("✅ Handit.ai configuration found!")
    print(f"🔑 API Key: {handit_api_key[:8]}...{handit_api_key[-4:] if len(handit_api_key) > 12 else '***'}")
    return True

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Check Handit.ai configuration before starting the server
    if not check_handit_configuration():
        print("")
        print("🚫 Server startup aborted. Please configure Handit.ai first.")
        exit(1)
    
    logger.info("🚀 Starting FastAPI Backend...")
    
    # Start the FastAPI server with uvicorn
    # Host "0.0.0.0" allows external connections (not just localhost)
    # Port 8000 is the default FastAPI development port
    uvicorn.run(app, host="0.0.0.0", port=8000)