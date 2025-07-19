#!/usr/bin/env python3
"""
Dakshin Programming Language Compiler
Entry point for compiling Dakshin source files to assembly
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from compiler import compile_to_assembly

def main():
    """Main compilation interface"""
    if len(sys.argv) < 2:
        print("Dakshin Programming Language Compiler")
        print("Usage: python dakshin.py <source_file> [output_file]")
        print("")
        print("Examples:")
        print("  python dakshin.py program.dn              # Generate assembly in out/ directory")
        print("  python dakshin.py program.dn output.asm   # Write assembly to specific file")
        return
    
    source_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # If no output file specified, generate it in the out/ directory
    if output_file is None:
        # Ensure out/ directory exists
        out_dir = os.path.join(os.path.dirname(__file__), 'out')
        os.makedirs(out_dir, exist_ok=True)
        
        # Generate output filename based on source filename
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        output_file = os.path.join(out_dir, f"{base_name}.asm")
    
    compile_to_assembly(source_file, output_file)

if __name__ == "__main__":
    main()
