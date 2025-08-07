#!/usr/bin/env python3
"""
File Reading Utility - Intelligent File Content Extraction for Invoice Copilot

This module provides a robust file reading utility that supports reading entire files
or specific line ranges with automatic line numbering. It's designed to work seamlessly
with the Invoice Copilot system's file processing requirements.

Key Features:
- Flexible file reading (entire file or line ranges)
- Automatic 1-based line numbering for easy reference
- Comprehensive error handling and validation
- Support for both relative and absolute file paths
- UTF-8 encoding support for international content
- Line range validation and bounds checking
- Performance optimization with 250-line limit

Dependencies:
- os: Operating system interface for file operations
- typing: Type hints for better code quality

Configuration:
- Default encoding: UTF-8
- Maximum line range: 250 lines
- Line numbering: 1-based (human-readable)

Author: coderTtxi12
Version: 1.0.0
"""

import os
from typing import Tuple, Optional

def read_file(
    target_file: str, 
    start_line_one_indexed: Optional[int] = None, 
    end_line_one_indexed_inclusive: Optional[int] = None, 
    should_read_entire_file: bool = False
) -> Tuple[str, bool]:
    """
    Read content from a file with support for line ranges and automatic line numbering.
    
    This function provides flexible file reading capabilities for the Invoice Copilot
    system. It can read entire files or specific line ranges, automatically adding
    1-based line numbers to the output for easy reference and debugging.
    
    The function includes comprehensive validation to ensure safe file operations:
    - File existence checking
    - Line range validation
    - Bounds checking for requested line ranges
    - Performance limits (250 lines maximum)
    - Proper error handling and reporting
    
    Args:
        target_file (str): Path to the file (relative or absolute). The function
                          will check if the file exists before attempting to read.
        start_line_one_indexed (Optional[int]): Starting line number (1-based).
                                               If None, defaults to reading entire file.
                                               Must be >= 1 if specified.
        end_line_one_indexed_inclusive (Optional[int]): Ending line number (1-based).
                                                       If None, defaults to reading entire file.
                                                       Must be >= start_line_one_indexed.
        should_read_entire_file (bool): If True, ignore line parameters and read entire file.
                                       This takes precedence over line range parameters.
                                       Default: False
    
    Returns:
        Tuple[str, bool]: A tuple containing:
            - str: File content with line numbers (if successful) or error message (if failed)
            - bool: Success status (True for success, False for failure)
    
    Raises:
        No exceptions are raised - all errors are returned as part of the tuple
    
    Example:
        >>> # Read entire file
        >>> content, success = read_file("example.txt")
        >>> print(success)
        True
        >>> print(content[:50])
        "1: First line of the file
         2: Second line of the file..."
        
        >>> # Read specific line range
        >>> content, success = read_file("example.txt", 5, 10)
        >>> print(success)
        True
        >>> print(content)
        "5: Fifth line
         6: Sixth line
         7: Seventh line..."
        
        >>> # Read non-existent file
        >>> content, success = read_file("nonexistent.txt")
        >>> print(success)
        False
        >>> print(content)
        "Error: File nonexistent.txt does not exist"
    
    Note:
        - Uses UTF-8 encoding for all file operations
        - Automatically adds 1-based line numbers to output
        - Maximum line range is 250 lines for performance
        - Supports both relative and absolute file paths
        - Comprehensive error messages for debugging
        - Safe file operations with proper exception handling
    """
    try:
        # Check if the target file exists before attempting to read
        # This prevents unnecessary file operations and provides clear error messages
        if not os.path.exists(target_file):
            return f"Error: File {target_file} does not exist", False
        
        # Determine reading mode based on parameters
        # If any line parameter is None or should_read_entire_file is True,
        # read the entire file for simplicity and consistency
        if start_line_one_indexed is None or end_line_one_indexed_inclusive is None:
            should_read_entire_file = True
        
        # Open file with UTF-8 encoding for international content support
        with open(target_file, 'r', encoding='utf-8') as f:
            if should_read_entire_file:
                # Read all lines from the file
                lines = f.readlines()
                
                # Add 1-based line numbers to each line for easy reference
                # This helps with debugging and makes output more readable
                numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
                return ''.join(numbered_lines), True
            
            # Validate line range parameters for partial file reading
            # Ensure start_line is at least 1 (1-based indexing)
            if start_line_one_indexed < 1:
                return "Error: start_line_one_indexed must be at least 1", False
            
            # Ensure end_line is not before start_line
            if end_line_one_indexed_inclusive < start_line_one_indexed:
                return "Error: end_line_one_indexed_inclusive must be >= start_line_one_indexed", False
            
            # Check if requested range exceeds performance limit
            # This prevents memory issues with very large files
            if end_line_one_indexed_inclusive - start_line_one_indexed + 1 > 250:
                return "Error: Cannot read more than 250 lines at once", False
            
            # Read all lines from the file for line range processing
            lines = f.readlines()
            
            # Convert 1-based line numbers to 0-based array indices
            # This handles the conversion between human-readable line numbers and array indexing
            start_idx = start_line_one_indexed - 1
            end_idx = end_line_one_indexed_inclusive - 1
            
            # Check if the requested start line is beyond the file length
            # This prevents index out of bounds errors
            if start_idx >= len(lines):
                return f"Error: start_line_one_indexed ({start_line_one_indexed}) exceeds file length ({len(lines)})", False
            
            # Ensure end_idx doesn't exceed file bounds
            # This handles cases where the requested end line is beyond the file length
            end_idx = min(end_idx, len(lines) - 1)
            
            # Extract the requested line range and add line numbers
            # This creates the final output with proper line numbering
            numbered_lines = [f"{i+1}: {lines[i]}" for i in range(start_idx, end_idx + 1)]
            
            return ''.join(numbered_lines), True
            
    except Exception as e:
        # Catch all exceptions and return them as error messages
        # This ensures the function never raises exceptions and always returns a valid tuple
        return f"Error reading file: {str(e)}", False

# =============================================================================
# TESTING AND DEVELOPMENT
# =============================================================================

if __name__ == "__main__":
    """
    Test function for development and debugging.
    
    This section runs when the module is executed directly, providing
    comprehensive testing of the file reading functionality with various
    scenarios including edge cases and error conditions.
    """
    # Create a path to the dummy text file for testing
    dummy_file = "dummy_text.txt"
    
    # Test if dummy file exists before running tests
    # This prevents test failures due to missing test data
    if not os.path.exists(dummy_file):
        print(f"Dummy file {dummy_file} not found. Please create it first.")
        exit(1)
    
    # Test 1: Reading entire file with default parameters
    # This tests the most common use case
    print("=== Test 1: Reading entire file with default parameters ===")
    content, success = read_file(dummy_file)
    print(f"Success: {success}")
    print(f"Content preview: {content[:150]}..." if len(content) > 150 else f"Content: {content}")
    
    # Test 2: Reading entire file explicitly
    # This tests the explicit entire file reading mode
    print("\n=== Test 2: Reading entire file explicitly ===")
    content, success = read_file(dummy_file, should_read_entire_file=True)
    print(f"Success: {success}")
    print(f"Content preview: {content[:150]}..." if len(content) > 150 else f"Content: {content}")
    
    # Test 3: Reading specific line range
    # This tests the partial file reading functionality
    print("\n=== Test 3: Reading specific line range (lines 2-4) ===")
    content, success = read_file(dummy_file, 2, 4)
    print(f"Success: {success}")
    print(f"Content:\n{content}")
    
    # Test 4: Reading with invalid parameters
    # This tests error handling for invalid input
    print("\n=== Test 4: Reading with invalid start line (0) ===")
    content, success = read_file(dummy_file, 0, 5)
    print(f"Success: {success}")
    print(f"Message: {content}")
    
    # Test 5: Reading non-existent file
    # This tests error handling for missing files
    print("\n=== Test 5: Reading non-existent file ===")
    content, success = read_file("non_existent_file.txt")
    print(f"Success: {success}")
    print(f"Message: {content}")
    
    print("\n=== All tests completed ===") 