#!/usr/bin/env python3
import sys
import os

print("DEBUG: Starting dakshin compiler")
print(f"DEBUG: Arguments: {sys.argv}")
print(f"DEBUG: Working directory: {os.getcwd()}")

# Test basic imports
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    print("DEBUG: Added src to path")
    
    print("DEBUG: Importing modules...")
    from compiler import compile_to_assembly
    print("DEBUG: Import successful")
    
    if len(sys.argv) < 2:
        print("Dakshin Programming Language Compiler")
        print("Usage: python debug_dakshin.py <source_file>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    print(f"DEBUG: Compiling {source_file}")
    
    # Call the compiler
    result = compile_to_assembly(source_file)
    print(f"DEBUG: Compilation result: {result}")
    
except Exception as e:
    print(f"DEBUG: Error occurred: {e}")
    import traceback
    traceback.print_exc()
