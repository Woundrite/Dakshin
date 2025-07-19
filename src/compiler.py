"""
Integrated Code Generator for Dakshin Programming Language
Integrates with the parser to generate assembly from source files
"""

from Lexer import Lexer
from File import FileReader
from Error import ErrorHandler
from Parser import Parser
from ParsingTable import convert_token_types
from code_generator import AssemblyGenerator
import sys
import json

def compile_to_assembly(file_path, output_file=None):
    """Compile Dakshin source file to assembly"""
    try:
        # Initialize components
        error_handler = ErrorHandler()
        lexer = Lexer(error_handler)
        file_reader = FileReader(file_path=file_path)
        
        # Parse source code
        print(f"Compiling: {file_path}")
        print("Lexical Analysis...")
        tokens = lexer.tokenize(file_reader)
        
        print("Syntactic Analysis...")
        parsed_tokens = convert_token_types(tokens)
        parser = Parser(parsed_tokens)
        ast = parser.parse()
        
        print("Code Generation...")
        generator = AssemblyGenerator()
        assembly_code = generator.generate(ast)
        
        # Output assembly
        if output_file:
            with open(output_file, 'w') as f:
                f.write(assembly_code)
            print(f"✅ Assembly written to: {output_file}")
        else:
            print("Generated Assembly Code:")
            print("=" * 60)
            print(assembly_code)
        
        # Show compilation statistics
        print("\nCompilation Statistics:")
        print(f"• Source file: {file_path}")
        print(f"• Tokens processed: {len(tokens)}")
        print(f"• AST nodes: {count_ast_nodes(ast)}")
        print(f"• Assembly lines: {len(assembly_code.split(chr(10)))}")
        print(f"• String literals: {generator.string_counter}")
        
        return assembly_code
        
    except Exception as e:
        import traceback
        print(f"Compilation failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return None

def count_ast_nodes(ast):
    """Count total nodes in AST"""
    count = 0
    if isinstance(ast, list):
        for item in ast:
            count += count_ast_nodes(item)
    elif isinstance(ast, dict):
        count += 1
        for value in ast.values():
            count += count_ast_nodes(value)
    return count

def main():
    """Main compilation interface"""
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source_file> [output_file]")
        print("Example: python compiler.py test_constructor.dn output.asm")
        return
    
    source_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    compile_to_assembly(source_file, output_file)

if __name__ == "__main__":
    main()
