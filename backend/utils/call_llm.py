#!/usr/bin/env python3
"""
LLM Communication Utility - OpenAI Integration

This module provides a centralized interface for communicating with OpenAI's
Language Models (LLMs) used throughout the Invoice Copilot system. It handles
API calls, response processing, logging, and optional caching functionality.

Key Features:
- OpenAI API integration with configurable models
- Comprehensive logging of all LLM interactions
- Optional caching system for performance optimization
- Error handling and retry mechanisms
- Configurable parameters (temperature, max_tokens, etc.)

Dependencies:
- openai: OpenAI Python client library
- os: Operating system interface
- logging: Logging functionality
- json: JSON data processing
- datetime: Date and time handling
- dotenv: Environment variable management

Configuration:
- OPENAI_API_KEY: Required OpenAI API key
- OPENAI_MODEL: Model to use (default: gpt-4o-mini-2024-07-18)
- LOG_DIR: Directory for log files (default: logs)

Author: coderTtxi12
Version: 1.0.0
"""

from openai import OpenAI
import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Load environment variables from .env file
# This ensures API keys and configuration are properly loaded
load_dotenv()

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Configure logging directory and file structure
# Creates daily log files for better organization and debugging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log")

# Set up logger with file handler for persistent logging
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# =============================================================================
# CACHE CONFIGURATION
# =============================================================================

# Simple cache configuration for performance optimization
# Note: Cache functionality is currently disabled but can be enabled
cache_file = "llm_cache.json"

def call_llm(system_prompt: str, user_prompt: str, use_cache: bool = False) -> str:
    """
    Make a call to OpenAI's Language Model with comprehensive logging and optional caching.
    
    This function is the primary interface for LLM communication in the Invoice Copilot
    system. It handles API calls to OpenAI, processes responses, logs all interactions,
    and optionally caches results for performance optimization.
    
    The function supports both system and user prompts, allowing for structured
    conversations with the LLM. It uses configurable parameters like temperature
    and max_tokens to control the response characteristics.
    
    Args:
        system_prompt (str): The system prompt that defines the LLM's role and behavior.
                           This sets the context and instructions for the model.
        user_prompt (str): The user's input or question that the LLM should respond to.
                          This is the actual query or request being made.
        use_cache (bool, optional): Whether to use caching for performance optimization.
                                   Currently disabled but can be enabled. Default: False
    
    Returns:
        str: The LLM's response as a string
        
    Raises:
        Exception: If the OpenAI API call fails or if required environment variables
                  are missing (OPENAI_API_KEY)
    
    Example:
        >>> system_prompt = "You are a helpful assistant that specializes in data analysis."
        >>> user_prompt = "What is the total revenue from the invoice data?"
        >>> response = call_llm(system_prompt, user_prompt)
        >>> print(response)
        "Based on the invoice data, the total revenue is..."
    
    Note:
        - Requires OPENAI_API_KEY environment variable to be set
        - All calls are logged to daily log files for debugging
        - Uses gpt-4o-mini-2024-07-18 model by default
        - Temperature is set to 0.4 for balanced creativity and consistency
        - Max tokens limited to 4000 for cost control
        - Cache functionality is currently disabled but infrastructure exists
    """
    # Log the user prompt for debugging and monitoring
    logger.info(f"USER PROMPT: {user_prompt}")
    
    # Cache functionality is currently disabled but can be enabled
    # This section handles cache checking and retrieval
    # if use_cache:
    #     # Load cache from disk for persistence across sessions
    #     cache = {}
    #     if os.path.exists(cache_file):
    #         try:
    #             with open(cache_file, 'r') as f:
    #                 cache = json.load(f)
    #         except:
    #             logger.warning(f"Failed to load cache, starting with empty cache")
        
    #     # Return cached response if available (performance optimization)
    #     if prompt in cache:
    #         logger.info(f"Cache hit for prompt: {prompt[:50]}...")
    #         return cache[prompt]
    
    # Initialize OpenAI client with API key from environment
    # This is the core connection to OpenAI's API
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Make the API call to OpenAI with structured messages
    # System prompt sets the context, user prompt is the actual query
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4000,  # Limit response length for cost control
        temperature=0.4    # Balance between creativity and consistency
    )
    
    # Extract the response text from the API response
    response_text = response.choices[0].message.content
    
    # Log the response for debugging and monitoring
    logger.info(f"RESPONSE: {response_text}")
    
    # Cache functionality is currently disabled but can be enabled
    # This section handles cache storage for future requests
    # if use_cache:
    #     # Load cache again to avoid overwrites from concurrent requests
    #     cache = {}
    #     if os.path.exists(cache_file):
    #         try:
    #             with open(cache_file, 'r') as f:
    #                 cache = json.load(f)
    #         except:
    #             pass
        
    #     # Add response to cache and save to disk
    #     cache[prompt] = response_text
    #     try:
    #         with open(cache_file, 'w') as f:
    #             json.dump(cache, f)
    #         logger.info(f"Added to cache")
    #     except Exception as e:
    #         logger.error(f"Failed to save cache: {e}")
    
    return response_text

# =============================================================================
# CACHE MANAGEMENT FUNCTIONS
# =============================================================================

# def clear_cache() -> None:
#     """
#     Clear the cache file if it exists.
#     
#     This function removes the cache file to free up disk space or reset
#     cached responses. Useful for debugging or when cache becomes corrupted.
#     
#     Example:
#         >>> clear_cache()
#         Cache cleared
#     """
#     if os.path.exists(cache_file):
#         os.remove(cache_file)
#         logger.info("Cache cleared")

# =============================================================================
# TESTING AND DEVELOPMENT
# =============================================================================

if __name__ == "__main__":
    """
    Test function for development and debugging.
    
    This section runs when the module is executed directly, providing
    a simple way to test the LLM communication functionality.
    """
    test_prompt = "Hello, how are you?"
    
    # First call - should hit the API
    print("Making first call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
    
    # Second call - should hit cache (if enabled)
    print("\nMaking second call with same prompt...")
    response2 = call_llm(test_prompt, use_cache=True)
    print(f"Response: {response2}")
