#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from Lexer import Lexer
from Parser import Parser
from File import FileReader
from Error import ErrorHandler
from ParsingTable import convert_token_types
import json

def debug_parse(file_path):
    """Debug parser output for a specific file"""
    try:
        # Initialize components like the compiler does
        error_handler = ErrorHandler()
        lexer = Lexer(error_handler)
        file_reader = FileReader(file_path=file_path)
        
        # Tokenize
        print("Tokens:")
        tokens = lexer.tokenize(file_reader)
        for token in tokens:
            print(f"  {token}")
        print()
        
        # Parse
        print("Parsing...")
        parsed_tokens = convert_token_types(tokens)
        parser = Parser(parsed_tokens)
        ast = parser.parse()
        
        print("AST:")
        print(json.dumps(ast, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_lambda_parse.py <file.dn>")
        sys.exit(1)
    
    debug_parse(sys.argv[1])
