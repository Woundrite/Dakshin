#!/usr/bin/env python3
"""
Dakshin Programming Language REPL and Parser
Entry point for parsing and analyzing Dakshin source files
"""

import sys
import os

# Add src directory to path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import process_code
from Lexer import Lexer
from File import FileReader
from Error import ErrorHandler

def main():
    """Main parser interface"""
    if len(sys.argv) < 2:
        print("Dakshin Programming Language Parser")
        print("Usage: python parse.py <source_file>")
        print("")
        print("Examples:")
        print("  python parse.py program.dn    # Parse and show AST")
        return
    
    error_handler = ErrorHandler()
    lexer = Lexer(error_handler)
    file_path = sys.argv[1]
    file_reader = FileReader(file_path=file_path)
    process_code(lexer, file_reader)

if __name__ == "__main__":
    main()
