"""
Console setup utilities for the Assessment Tool.
Handles UTF-8 encoding configuration for Windows console output.
"""

import sys
import os


def setup_console_encoding():
    """Configure UTF-8 encoding for Windows console output (emoji and Unicode support)."""
    if sys.platform == 'win32':
        import io
        # Use line_buffering=False to ensure spinner animations work with flush()
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, 
            encoding='utf-8', 
            errors='replace', 
            line_buffering=False
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, 
            encoding='utf-8', 
            errors='replace', 
            line_buffering=False
        )
        os.environ['PYTHONIOENCODING'] = 'utf-8'
