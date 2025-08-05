#!/usr/bin/env python3
"""
Simple FastAPI Backend
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Chunkr
chunkr = Chunkr()



app = FastAPI(
    title="FastAPI Backend",
    description="FastAPI backend with health endpoint",
    version="1.0.0"
)

# CORS configuration - only allow specific origins
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("🏥 Health check requested")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

async def process_file_with_chunkr(chunkr, file_path: Path, output_dir: Path):
    """Process a single file with Chunkr AI"""
    try:
        logger.info(f"📄 Processing file: {file_path.name}")
        
        # Upload file to Chunkr
        result = await chunkr.upload(file_path)
        
        # Check if upload was successful
        if result.status == "Failed":
            logger.error(f"❌ Failed to process file {file_path.name}: {result.message}")
            return {
                "file_name": file_path.name,
                "status": "failed",
                "error": result.message
            }
        
        # Save result to output directory
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



@app.post("/api/documents/bulk-process")
async def bulk_document_processing(
    files: List[UploadFile] = File(...),
    output_dir: Optional[str] = None
):
    """
    Bulk document processing endpoint using Chunkr AI
    
    - **files**: List of files to process
    - **output_dir**: Optional output directory (defaults to 'processed/')
    """
    logger.info(f"📄 Bulk document processing requested - {len(files)} files")
    
    try:
        # Set default output directory
        if output_dir is None:
            output_dir = "processed"
        
        # Create output directory
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        # Create temporary directory for uploaded files
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
            
            # Process files concurrently
            tasks = []
            for file_path in saved_files:
                task = asyncio.create_task(
                    process_file_with_chunkr(chunkr, file_path, output_path)
                )
                tasks.append(task)
            
            # Wait for all files to complete
            results = await asyncio.gather(*tasks)
            
            # Count successful and failed processing
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

@app.post("/api/documents/process-directory")
async def process_directory_endpoint(
    input_dir: str,
    output_dir: Optional[str] = None
):
    """
    Process all documents in a directory using Chunkr AI
    
    - **input_dir**: Directory path containing files to process
    - **output_dir**: Optional output directory (defaults to 'processed/')
    """
    logger.info(f"📁 Directory processing requested: {input_dir}")
    
    try:
        # Validate input directory
        input_path = Path(input_dir)
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Input directory does not exist: {input_dir}")
        
        # Set default output directory
        if output_dir is None:
            output_dir = "processed"
        
        # Create output directory
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        # Get all files in directory
        files = list(input_path.glob('*.*'))
        logger.info(f"📄 Found {len(files)} files to process")
        
        if not files:
            return {
                "message": "No files found in directory",
                "input_directory": str(input_path),
                "total_files": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Process files concurrently
        tasks = []
        for file_path in files:
            task = asyncio.create_task(
                process_file_with_chunkr(chunkr, file_path, output_path)
            )
            tasks.append(task)
        
        # Wait for all files to complete
        results = await asyncio.gather(*tasks)
        
        # Count successful and failed processing
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
        raise
    except Exception as e:
        logger.error(f"❌ Error in directory processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing directory: {str(e)}")



# Import the coding agent
try:
    from agent import CodingAgent
    agent_available = True
    logger.info("✅ Coding agent imported successfully")
except ImportError as e:
    agent_available = False
    logger.warning(f"⚠️ Coding agent not available: {str(e)}")

@app.post("/api/chat/message")
async def process_chat_message(message: dict):
    """
    Process chat messages using the coding agent
    
    - **message**: Dictionary containing user message and optional parameters
    """
    try:
        user_message = message.get("message", "")
        workspace_dir = message.get("workspace_dir", "frontend/src/components/workspace/DynamicWorkspace.tsx")
        max_iterations = message.get("max_iterations", 10)
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if not agent_available:
            return {
                "success": False,
                "error": "Coding agent not available",
                "response": "I'm sorry, but the coding agent is not currently available. Please check the backend configuration."
            }
        
        logger.info(f"💬 Processing chat message: {user_message}")
        logger.info(f"📁 Working directory: {workspace_dir}")
        
        # Initialize the coding agent with the workspace directory
        agent = CodingAgent(working_dir=workspace_dir)
        
        # Process the user's message
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

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)