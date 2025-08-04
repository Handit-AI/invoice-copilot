import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pinecone import Pinecone

# Set up logging
logger = logging.getLogger(__name__)

def semantic_search(
    query: str,
    namespace: str = "example-namespace",
    top_k: int = 10,
    index_name: Optional[str] = None,
    api_key: Optional[str] = None,
    include_metadata: bool = True,
    include_values: bool = False
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Perform semantic search using Pinecone's integrated embeddings.
    
    Args:
        query: The text query to search for
        namespace: Pinecone namespace to search in
        top_k: Number of top results to return (max 10000)
        index_name: Pinecone index name (defaults to env var PINECONE_INDEX_NAME)
        api_key: Pinecone API key (defaults to env var PINECONE_API_KEY)
        include_metadata: Whether to include metadata in results
        include_values: Whether to include vector values in results
        
    Returns:
        Tuple of (success: bool, results: List[Dict[str, Any]])
        
    Example:
        success, results = semantic_search("Famous historical structures", top_k=5)
        if success:
            for result in results:
                print(f"Score: {result['score']}, Text: {result['metadata']['content']}")
    """
    try:
        # Get configuration from environment or parameters
        pinecone_api_key = api_key or os.getenv("PINECONE_API_KEY")
        pinecone_index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "invoice-copilot")
        
        if not pinecone_api_key:
            logger.error("Pinecone API key not provided")
            return False, []
        
        if not pinecone_index_name:
            logger.error("Pinecone index name not provided")
            return False, []
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=pinecone_api_key)
        
        # Get the index
        index = pc.Index(pinecone_index_name)
        
        logger.info(f"🔍 Performing semantic search for: '{query}' in namespace '{namespace}'")
        
        # Perform the search using Pinecone's integrated embeddings
        search_response = index.search(
            namespace=namespace,
            query={
                "top_k": min(top_k, 10000),  # Pinecone limit
                "inputs": {
                    'text': query
                }
            },
            include_metadata=include_metadata,
            include_values=include_values
        )
        
        # Process the results
        hits = search_response.get('result', {}).get('hits', [])
        
        processed_results = []
        for hit in hits:
            result = {
                "id": hit.get('_id', ''),
                "score": hit.get('_score', 0.0),
                "metadata": hit.get('fields', {}) if include_metadata else {}
            }
            
            # Include vector values if requested
            if include_values and 'values' in hit:
                result["values"] = hit['values']
            
            processed_results.append(result)
        
        logger.info(f"✅ Found {len(processed_results)} results for query: '{query}'")
        return True, processed_results
        
    except Exception as e:
        logger.error(f"❌ Error performing semantic search: {str(e)}")
        return False, []


def format_search_results(results: List[Dict[str, Any]], max_text_length: int = 100) -> str:
    """
    Format search results into a readable string.
    
    Args:
        results: List of search results from semantic_search()
        max_text_length: Maximum length of text to display per result
        
    Returns:
        Formatted string with search results
    """
    if not results:
        return "No results found."
    
    formatted_lines = []
    formatted_lines.append(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        result_id = result.get('id', 'N/A')
        score = result.get('score', 0.0)
        metadata = result.get('metadata', {})
        
        # Extract common metadata fields
        category = metadata.get('category', 'N/A')
        content = metadata.get('content', metadata.get('chunk_text', 'N/A'))
        original_filename = metadata.get('original_filename', 'N/A')
        
        # Truncate content if too long
        if len(content) > max_text_length:
            content = content[:max_text_length] + "..."
        
        formatted_lines.append(
            f"{i:2d}. ID: {result_id:<10} | Score: {score:.3f} | "
            f"Category: {category:<12} | File: {original_filename:<20} | "
            f"Text: {content}"
        )
    
    return "\n".join(formatted_lines)


def search_by_category(
    query: str,
    category: str,
    namespace: str = "example-namespace",
    top_k: int = 10,
    index_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Perform semantic search filtered by category using metadata filtering.
    
    Args:
        query: The text query to search for
        category: Category to filter by
        namespace: Pinecone namespace to search in
        top_k: Number of top results to return
        index_name: Pinecone index name (defaults to env var)
        api_key: Pinecone API key (defaults to env var)
        
    Returns:
        Tuple of (success: bool, results: List[Dict[str, Any]])
    """
    try:
        # Get configuration from environment or parameters
        pinecone_api_key = api_key or os.getenv("PINECONE_API_KEY")
        pinecone_index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "invoice-copilot")
        
        if not pinecone_api_key:
            logger.error("Pinecone API key not provided")
            return False, []
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)
        
        logger.info(f"🔍 Searching for: '{query}' in category: '{category}'")
        
        # Perform search with metadata filter
        search_response = index.search(
            namespace=namespace,
            query={
                "top_k": min(top_k, 10000),
                "inputs": {
                    'text': query
                },
                "filter": {
                    "category": {"$eq": category}
                }
            },
            include_metadata=True
        )
        
        # Process results
        hits = search_response.get('result', {}).get('hits', [])
        processed_results = []
        
        for hit in hits:
            result = {
                "id": hit.get('_id', ''),
                "score": hit.get('_score', 0.0),
                "metadata": hit.get('fields', {})
            }
            processed_results.append(result)
        
        logger.info(f"✅ Found {len(processed_results)} results in category '{category}'")
        return True, processed_results
        
    except Exception as e:
        logger.error(f"❌ Error performing category search: {str(e)}")
        return False, []


def search_by_filename(
    query: str,
    filename: str,
    namespace: str = "example-namespace",
    top_k: int = 10,
    index_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Perform semantic search within a specific file.
    
    Args:
        query: The text query to search for
        filename: Original filename to search within
        namespace: Pinecone namespace to search in
        top_k: Number of top results to return
        index_name: Pinecone index name (defaults to env var)
        api_key: Pinecone API key (defaults to env var)
        
    Returns:
        Tuple of (success: bool, results: List[Dict[str, Any]])
    """
    try:
        # Get configuration from environment or parameters
        pinecone_api_key = api_key or os.getenv("PINECONE_API_KEY")
        pinecone_index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "invoice-copilot")
        
        if not pinecone_api_key:
            logger.error("Pinecone API key not provided")
            return False, []
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)
        
        logger.info(f"🔍 Searching for: '{query}' in file: '{filename}'")
        
        # Perform search with filename filter
        search_response = index.search(
            namespace=namespace,
            query={
                "top_k": min(top_k, 10000),
                "inputs": {
                    'text': query
                },
                "filter": {
                    "original_filename": {"$eq": filename}
                }
            },
            include_metadata=True
        )
        
        # Process results
        hits = search_response.get('result', {}).get('hits', [])
        processed_results = []
        
        for hit in hits:
            result = {
                "id": hit.get('_id', ''),
                "score": hit.get('_score', 0.0),
                "metadata": hit.get('fields', {})
            }
            processed_results.append(result)
        
        logger.info(f"✅ Found {len(processed_results)} results in file '{filename}'")
        return True, processed_results
        
    except Exception as e:
        logger.error(f"❌ Error performing filename search: {str(e)}")
        return False, []


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic semantic search
    print("=== Basic Semantic Search ===")
    success, results = semantic_search("Famous historical structures and monuments", top_k=5)
    if success:
        print(format_search_results(results))
    else:
        print("Search failed")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Search by category
    print("=== Search by Category ===")
    success, results = search_by_category("historical buildings", "history", top_k=3)
    if success:
        print(format_search_results(results))
    else:
        print("Category search failed")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Search within specific file
    print("=== Search by Filename ===")
    success, results = search_by_filename("invoice total", "invoice_001.pdf", top_k=3)
    if success:
        print(format_search_results(results))
    else:
        print("Filename search failed")
