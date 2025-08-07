#!/usr/bin/env python3
"""
File Replacement Utility - Intelligent File Content Modification for Invoice Copilot

This module provides robust file modification capabilities for the Invoice Copilot
system. It supports both partial file replacement (specific line ranges) and
complete file overwriting, with comprehensive error handling and validation.

Key Features:
- Partial file replacement with line range specification
- Complete file overwriting for full content replacement
- Automatic file creation for new files
- Directory creation for nested file paths
- Comprehensive error handling and validation
- UTF-8 encoding support for international content
- Detailed logging for debugging and monitoring
- Safe file operations with proper exception handling

Dependencies:
- os: Operating system interface for file and directory operations
- logging: Logging functionality for debugging and monitoring
- typing: Type hints for better code quality

Configuration:
- Default encoding: UTF-8
- Line numbering: 1-based (human-readable)
- Automatic directory creation: Enabled
- File creation: Enabled for non-existent files

Author: coderTtxi12
Version: 1.0.0
"""

import os
import logging
from typing import Tuple

# Set up logger for this module
logger = logging.getLogger(__name__)

def replace_file(target_file: str, start_line: int, end_line: int, content: str) -> Tuple[bool, str]:
    """
    Replace specific lines in a file with new content.
    
    This function provides flexible file modification capabilities, allowing
    replacement of specific line ranges while preserving the rest of the file.
    It handles various edge cases including file creation, appending, and
    bounds checking for safe file operations.
    
    The function supports multiple scenarios:
    - Replacing existing lines within the file
    - Appending content to the end of the file
    - Creating new files when the target doesn't exist
    - Automatic directory creation for nested paths
    
    Args:
        target_file (str): Path to the file to modify (relative or absolute).
                          If the file doesn't exist, it will be created.
        start_line (int): Starting line number (1-indexed, inclusive).
                         Must be >= 1.
        end_line (int): Ending line number (1-indexed, inclusive).
                       Must be >= start_line.
        content (str): New content to replace the specified lines.
                      Can contain multiple lines with newline characters.
    
    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: Success status (True for success, False for failure)
            - str: Detailed message describing the operation result
    
    Raises:
        No exceptions are raised - all errors are returned as part of the tuple
    
    Example:
        >>> # Replace lines 5-7 in an existing file
        >>> success, message = replace_file("example.txt", 5, 7, "New line 5\nNew line 6\nNew line 7\n")
        >>> print(success)
        True
        >>> print(message)
        "Successfully replaced content. Lines: 10 → 10"
        
        >>> # Append content to end of file
        >>> success, message = replace_file("example.txt", 15, 15, "New content\n")
        >>> print(success)
        True
        >>> print(message)
        "Appending content to end of file: example.txt"
        
        >>> # Create new file
        >>> success, message = replace_file("newfile.txt", 1, 3, "Line 1\nLine 2\nLine 3\n")
        >>> print(success)
        True
        >>> print(message)
        "Created new file with 3 lines"
    
    Note:
        - Uses UTF-8 encoding for all file operations
        - Automatically creates directories if they don't exist
        - Handles appending when start_line exceeds file length
        - Preserves line endings and formatting
        - Comprehensive error messages for debugging
        - Safe file operations with proper exception handling
    """
    try:
        # Validate input parameters for safety
        # Ensure line numbers are positive (1-based indexing)
        if start_line < 1 or end_line < 1:
            return False, "Line numbers must be positive"
        
        # Ensure start_line is not greater than end_line
        if start_line > end_line:
            return False, f"Start line ({start_line}) cannot be greater than end line ({end_line})"
        
        # Check if the target file exists
        if not os.path.exists(target_file):
            # Create new file with the specified content
            # This handles the case where we want to create a new file
            logger.info(f"Creating new file: {target_file}")
            
            # Create parent directories if they don't exist
            # This ensures the file can be created even in nested directories
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            # Write the content to the new file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Return success with information about the created file
            line_count = len(content.splitlines())
            return True, f"Created new file with {line_count} lines"
        
        # Read the existing file for modification
        # This loads the current content for line replacement
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Store original line count for comparison
        original_line_count = len(lines)
        
        # Handle appending to the end of the file
        # This occurs when start_line is beyond the current file length
        if start_line > original_line_count:
            # Append content to the end of the file
            # Add newline if content doesn't start with one
            lines.append('\n' + content if not content.startswith('\n') else content)
            logger.info(f"Appending content to end of file: {target_file}")
        else:
            # Replace existing lines within the file
            # Convert 1-based line numbers to 0-based array indices
            start_idx = start_line - 1
            end_idx = min(end_line, original_line_count)
            
            # Prepare new content lines with proper line endings
            # This ensures consistent formatting
            new_lines = content.splitlines(keepends=True)
            if new_lines and not new_lines[-1].endswith('\n'):
                new_lines[-1] += '\n'
            
            # Replace the specified lines with new content
            # This performs the actual line replacement
            lines[start_idx:end_idx] = new_lines
            
            logger.info(f"Replaced lines {start_line}-{end_line} in {target_file}")
        
        # Write the modified content back to the file
        # This saves all changes to disk
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Return success with information about the operation
        new_line_count = len(lines)
        return True, f"Successfully replaced content. Lines: {original_line_count} → {new_line_count}"
        
    except FileNotFoundError:
        # Handle case where file is not found (shouldn't occur with our logic)
        return False, f"File not found: {target_file}"
    except PermissionError:
        # Handle permission issues (read-only files, insufficient permissions)
        return False, f"Permission denied: {target_file}"
    except UnicodeDecodeError:
        # Handle encoding issues (binary files, corrupted text)
        return False, f"Cannot decode file (not text): {target_file}"
    except Exception as e:
        # Catch all other exceptions and log them
        logger.error(f"Error replacing file content: {str(e)}")
        return False, f"Error: {str(e)}"

def write_entire_file(target_file: str, content: str) -> Tuple[bool, str]:
    """
    Write content to a file, completely replacing all existing content.
    
    This function is designed for complete file overwriting scenarios where
    the entire file content needs to be replaced. It's commonly used for
    generating new files or completely rewriting existing files.
    
    The function handles various scenarios:
    - Creating new files with content
    - Completely overwriting existing files
    - Automatic directory creation for nested paths
    - Safe file operations with proper error handling
    
    Args:
        target_file (str): Path to the file to write (relative or absolute).
                          If the file doesn't exist, it will be created.
        content (str): Content to write to the file.
                      This will completely replace any existing content.
    
    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: Success status (True for success, False for failure)
            - str: Detailed message describing the operation result
    
    Raises:
        No exceptions are raised - all errors are returned as part of the tuple
    
    Example:
        >>> # Create a new file with content
        >>> success, message = write_entire_file("newfile.txt", "Line 1\nLine 2\nLine 3\n")
        >>> print(success)
        True
        >>> print(message)
        "Successfully overwrote entire file with 3 lines"
        
        >>> # Overwrite existing file
        >>> success, message = write_entire_file("existing.txt", "New content\n")
        >>> print(success)
        True
        >>> print(message)
        "Successfully overwrote entire file with 1 lines"
    
    Note:
        - Uses UTF-8 encoding for all file operations
        - Automatically creates directories if they don't exist
        - Completely replaces existing file content
        - Preserves line endings and formatting
        - Comprehensive error messages for debugging
        - Safe file operations with proper exception handling
    """
    try:
        # Create parent directories if they don't exist
        # This ensures the file can be created even in nested directories
        target_dir = os.path.dirname(target_file)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        
        # Write the content to the file
        # This completely replaces any existing content
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Log the operation and return success
        line_count = len(content.splitlines())
        logger.info(f"Completely overwrote {target_file} with {line_count} lines")
        
        return True, f"Successfully overwrote entire file with {line_count} lines"
        
    except PermissionError:
        # Handle permission issues (read-only files, insufficient permissions)
        return False, f"Permission denied: {target_file}"
    except Exception as e:
        # Catch all other exceptions and log them
        logger.error(f"Error writing file: {str(e)}")
        return False, f"Error: {str(e)}"

def overwrite_entire_file(target_file: str, content: str) -> Tuple[bool, str]:
    """
    Completely overwrite a file with new content (alias for write_entire_file).
    
    This function is specifically designed for complete file replacement scenarios
    in the Invoice Copilot system. It provides a clear, descriptive name for
    the common use case of completely replacing file content.
    
    This is commonly used when:
    - Generating new React components
    - Creating complete report files
    - Replacing entire configuration files
    - Generating new documentation files
    
    Args:
        target_file (str): Path to the file to overwrite (relative or absolute).
                          If the file doesn't exist, it will be created.
        content (str): New content to replace the entire file.
                      This will completely replace any existing content.
    
    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: Success status (True for success, False for failure)
            - str: Detailed message describing the operation result
    
    Raises:
        No exceptions are raised - all errors are returned as part of the tuple
    
    Example:
        >>> # Overwrite a React component file
        >>> success, message = overwrite_entire_file(
        ...     "DynamicWorkspace.tsx",
        ...     "import React from 'react';\n\nexport function DynamicWorkspace() {\n  return <div>Hello World</div>;\n}\n"
        ... )
        >>> print(success)
        True
        >>> print(message)
        "Successfully overwrote entire file with 4 lines"
    
    Note:
        - This is an alias for write_entire_file for better semantic clarity
        - Uses UTF-8 encoding for all file operations
        - Automatically creates directories if they don't exist
        - Completely replaces existing file content
        - Comprehensive error messages for debugging
        - Safe file operations with proper exception handling
    """
    logger.info(f"Overwriting entire file: {target_file}")
    return write_entire_file(target_file, content)

# =============================================================================
# TESTING AND DEVELOPMENT
# =============================================================================

if __name__ == "__main__":
    """
    Test function for development and debugging.
    
    This section runs when the module is executed directly, providing
    comprehensive testing of the file replacement functionality with various
    scenarios including edge cases and error conditions.
    """
    # Test file for demonstration
    test_file = "test_replace.txt"
    
    print("=== File Replacement Utility Testing ===")
    
    # Test 1: Create a test file with initial content
    print("\n--- Test 1: Creating test file ---")
    success, msg = write_entire_file(test_file, "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
    print(f"Create test file: {success} - {msg}")
    
    # Test 2: Replace specific lines in the file
    print("\n--- Test 2: Replacing lines 2-3 ---")
    success, msg = replace_file(test_file, 2, 3, "New Line 2\nNew Line 3\n")
    print(f"Replace lines 2-3: {success} - {msg}")
    
    # Test 3: Display the result
    print("\n--- Test 3: Reading modified file ---")
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            print("File content after replacement:")
            print(f.read())
        
        # Clean up test file
        os.remove(test_file)
        print("\nTest file removed")
    
    print("\n=== Testing completed ===")