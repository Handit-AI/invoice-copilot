"""
File replacement utility for the coding agent.
This utility handles replacing specific lines in files.
"""

import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def replace_file(target_file: str, start_line: int, end_line: int, content: str) -> Tuple[bool, str]:
    """
    Replace lines in a file with new content.
    
    Args:
        target_file: Path to the file to modify
        start_line: Starting line number (1-indexed, inclusive)
        end_line: Ending line number (1-indexed, inclusive)
        content: New content to replace the lines
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Validate inputs
        if start_line < 1 or end_line < 1:
            return False, "Line numbers must be positive"
        
        if start_line > end_line:
            return False, f"Start line ({start_line}) cannot be greater than end line ({end_line})"
        
        # Check if file exists
        if not os.path.exists(target_file):
            # If file doesn't exist, create it with the content
            logger.info(f"Creating new file: {target_file}")
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Created new file with {len(content.splitlines())} lines"
        
        # Read the existing file
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_line_count = len(lines)
        
        # Handle case where we're appending to the file
        if start_line > original_line_count:
            # Append to the end of the file
            lines.append('\n' + content if not content.startswith('\n') else content)
            logger.info(f"Appending content to end of file: {target_file}")
        else:
            # Convert to 0-indexed for list operations
            start_idx = start_line - 1
            end_idx = min(end_line, original_line_count)
            
            # Prepare new content lines
            new_lines = content.splitlines(keepends=True)
            if new_lines and not new_lines[-1].endswith('\n'):
                new_lines[-1] += '\n'
            
            # Replace the specified lines
            lines[start_idx:end_idx] = new_lines
            
            logger.info(f"Replaced lines {start_line}-{end_line} in {target_file}")
        
        # Write the modified content back to the file
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        new_line_count = len(lines)
        return True, f"Successfully replaced content. Lines: {original_line_count} → {new_line_count}"
        
    except FileNotFoundError:
        return False, f"File not found: {target_file}"
    except PermissionError:
        return False, f"Permission denied: {target_file}"
    except UnicodeDecodeError:
        return False, f"Cannot decode file (not text): {target_file}"
    except Exception as e:
        logger.error(f"Error replacing file content: {str(e)}")
        return False, f"Error: {str(e)}"

def write_entire_file(target_file: str, content: str) -> Tuple[bool, str]:
    """
    Write content to a file, replacing all existing content.
    
    Args:
        target_file: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        # Write the content
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        line_count = len(content.splitlines())
        logger.info(f"Wrote {line_count} lines to {target_file}")
        
        return True, f"Successfully wrote {line_count} lines to file"
        
    except PermissionError:
        return False, f"Permission denied: {target_file}"
    except Exception as e:
        logger.error(f"Error writing file: {str(e)}")
        return False, f"Error: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    # Test the replace_file function
    test_file = "test_replace.txt"
    
    # Create a test file
    success, msg = write_entire_file(test_file, "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
    print(f"Create test file: {success} - {msg}")
    
    # Replace some lines
    success, msg = replace_file(test_file, 2, 3, "New Line 2\nNew Line 3\n")
    print(f"Replace lines 2-3: {success} - {msg}")
    
    # Read and display the result
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            print("File content after replacement:")
            print(f.read())
        
        # Clean up
        os.remove(test_file)
        print("Test file removed")