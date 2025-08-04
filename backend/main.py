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
from pinecone import Pinecone, ServerlessSpec
import uuid
import time
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Chunkr
chunkr = Chunkr()

# Initialize Pinecone (you'll need to set these environment variables)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "invoice-copilot")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Pinecone client
pc = None
if PINECONE_API_KEY:
    pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize OpenAI client
openai_client = None
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

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

async def get_openai_embedding(text: str):
    """Get embedding using OpenAI text-embedding-ada-002"""
    try:
        if not openai_client:
            raise Exception("OpenAI client not initialized")
        
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"❌ Error getting OpenAI embedding: {str(e)}")
        return None

async def store_segments_in_pinecone(json_file_path: Path, original_filename: str):
    """Store document segments in Pinecone vector database"""
    try:
        if not pc or not openai_client:
            logger.warning("⚠️ Pinecone or OpenAI not configured, skipping vector storage")
            return {"status": "skipped", "reason": "Pinecone or OpenAI not configured"}
        
        logger.info(f"🔍 Processing segments from {json_file_path.name}")
        
        # Read the JSON file
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Extract segments from the output
        segments = []
        if 'output' in data and 'chunks' in data['output']:
            for chunk in data['output']['chunks']:
                if 'segments' in chunk:
                    segments.extend(chunk['segments'])
        
        # Get index
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Use OpenAI text-embedding-ada-002 for embeddings
        logger.info("🚀 Using OpenAI text-embedding-ada-002 for embeddings...")
        
        # Prepare vectors with OpenAI embeddings
        vectors = []
        successful_vectors = 0
        failed_vectors = 0
        
        for i, segment in enumerate(segments):
            try:
                # Create text content
                text_content = segment.get('content', '') or segment.get('text', '')
                
                if not text_content:
                    logger.warning(f"⚠️ Skipping segment {i}: no content")
                    failed_vectors += 1
                    continue
                
                # Get OpenAI embedding
                embedding = await get_openai_embedding(text_content)
                if embedding is None:
                    failed_vectors += 1
                    continue
                
                # Create unique ID
                segment_id = segment.get('segment_id', str(uuid.uuid4()))
                
                # Create metadata
                metadata = {
                    "original_filename": original_filename,
                    "segment_type": segment.get('segment_type', 'document'),
                    "page_number": segment.get('page_number', 1),
                    "content": text_content[:1000],  # First 1000 chars for metadata
                    "confidence": segment.get('confidence')
                }
                
                # Clean metadata (remove None values)
                metadata = {k: v for k, v in metadata.items() if v is not None}
                
                # Create vector
                vector = {
                    "id": segment_id,
                    "values": embedding,
                    "metadata": metadata
                }
                
                vectors.append(vector)
                successful_vectors += 1
                
                if (i + 1) % 10 == 0:
                    logger.info(f"📄 Processed {i + 1}/{len(segments)} segments...")
                
            except Exception as e:
                logger.error(f"❌ Error processing segment {i}: {str(e)}")
                failed_vectors += 1
        
        if not vectors:
            return {"status": "error", "error": "No valid vectors to upsert"}
        
        try:
            # Upsert vectors to Pinecone in batches
            batch_size = 100
            total_upserted = 0
            
            logger.info(f"📤 Upserting {len(vectors)} vectors in batches of {batch_size}...")
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                
                response = index.upsert(vectors=batch)
                total_upserted += len(batch)
                
                logger.info(f"📤 Upserted batch {i//batch_size + 1}: {len(batch)} vectors")
            
            # Wait for indexing
            logger.info("⏳ Waiting for vectors to be indexed...")
            time.sleep(5)
            
            # Check stats
            stats = index.describe_index_stats()
            total_vector_count = stats.get('total_vector_count', 0)
            
            logger.info(f"✅ Success: {total_upserted} vectors upserted. Total in index: {total_vector_count}")
            
            # Clean stats to remove non-serializable objects
            clean_stats = {
                "total_vector_count": total_vector_count,
                "dimension": stats.get('dimension'),
                "index_fullness": stats.get('index_fullness')
            }
            
            return {
                "status": "success",
                "total_segments": len(segments),
                "successful_vectors": successful_vectors,
                "failed_vectors": failed_vectors,
                "total_upserted": total_upserted,
                "method": "openai_text_embedding_3_small_1024d",
                "index_stats": clean_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error upserting vectors: {str(e)}")
            return {"status": "error", "error": str(e)}
        
    except Exception as e:
        logger.error(f"❌ Error storing segments in Pinecone: {str(e)}")
        return {"status": "error", "error": str(e)}

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
            
            # Store successful results in Pinecone
            vector_results = []
            if successful:
                logger.info("🔍 Starting vector storage in Pinecone...")
                vector_tasks = []
                
                for result in successful:
                    if "output_file" in result:
                        json_file_path = Path(result["output_file"])
                        original_filename = result["file_name"]
                        
                        vector_task = asyncio.create_task(
                            store_segments_in_pinecone(json_file_path, original_filename)
                        )
                        vector_tasks.append(vector_task)
                
                # Wait for all vector storage tasks to complete
                vector_results = await asyncio.gather(*vector_tasks)
                
                logger.info(f"🔍 Vector storage completed for {len(vector_results)} files")
            
            return {
                "message": "Bulk document processing completed",
                "total_files": len(files),
                "successful": len(successful),
                "failed": len(failed),
                "output_directory": str(output_path),
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "vector_storage": vector_results
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

@app.post("/api/vectors/store-existing-json")
async def store_existing_json_in_pinecone(
    json_dir: Optional[str] = "processed"
):
    """
    Store existing JSON files from processed directory in Pinecone
    
    - **json_dir**: Directory containing JSON files (defaults to 'processed/')
    """
    logger.info(f"🔍 Storing existing JSON files from {json_dir} in Pinecone")
    
    try:
        # Validate directory
        json_path = Path(json_dir)
        if not json_path.exists():
            raise HTTPException(status_code=400, detail=f"Directory does not exist: {json_dir}")
        
        # Get all JSON files
        json_files = list(json_path.glob('*.json'))
        logger.info(f"📄 Found {len(json_files)} JSON files to process")
        
        if not json_files:
            return {
                "message": "No JSON files found in directory",
                "directory": str(json_path),
                "total_files": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Process files concurrently
        vector_tasks = []
        for json_file in json_files:
            # Extract original filename from JSON filename (remove .json extension)
            original_filename = json_file.stem
            
            vector_task = asyncio.create_task(
                store_segments_in_pinecone(json_file, original_filename)
            )
            vector_tasks.append(vector_task)
        
        # Wait for all vector storage tasks to complete
        vector_results = await asyncio.gather(*vector_tasks)
        
        # Count results
        successful_storage = [r for r in vector_results if r["status"] == "success"]
        failed_storage = [r for r in vector_results if r["status"] in ["error", "skipped"]]
        
        # Calculate total vectors stored
        total_vectors_stored = sum(r.get("total_upserted", 0) for r in successful_storage)
        
        logger.info(f"✅ Vector storage completed: {len(successful_storage)} files successful, {len(failed_storage)} failed")
        
        return {
            "message": "JSON files vector storage completed",
            "directory": str(json_path),
            "total_files": len(json_files),
            "successful_storage": len(successful_storage),
            "failed_storage": len(failed_storage),
            "total_vectors_stored": total_vectors_stored,
            "timestamp": datetime.now().isoformat(),
            "results": vector_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error storing JSON files in Pinecone: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error storing JSON files: {str(e)}")

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
        workspace_dir = message.get("workspace_dir", "frontend/src/components/workspace")
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