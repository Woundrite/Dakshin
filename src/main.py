from Lexer import Lexer
from File import FileReader
from Error import ErrorHandler
from Parser import Parser
from ParsingTable import convert_token_types

def process_code(lexer, file_reader):
    """Tokenize and print tokens for the given file reader."""
    try:
        tokens = lexer.tokenize(file_reader)
        # for token in tokens:
        #     print(token)
        parsed_tokens = convert_token_types(tokens)
        parser = Parser(parsed_tokens)
        import json
        ast_result = parser.parse()
        print(json.dumps(ast_result, indent=2))
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        # Print some context about where the error occurred
        if hasattr(parser, 'pos') and hasattr(parser, 'tokens'):
            print(f"Error position: {parser.pos}")
            if parser.pos < len(parser.tokens):
                print(f"Current token: {parser.tokens[parser.pos]}")
                # Show a few tokens around the error
                start = max(0, parser.pos - 3)
                end = min(len(parser.tokens), parser.pos + 3)
                print("Context:")
                for i in range(start, end):
                    marker = " -> " if i == parser.pos else "    "
                    print(f"{marker}{i}: {parser.tokens[i]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys

    error_handler = ErrorHandler()
    lexer = Lexer(error_handler)

    if len(sys.argv) > 1:  # File path passed as argument
        file_path = sys.argv[1]
        file_reader = FileReader(file_path=file_path)
        process_code(lexer, file_reader)
    else:  # No arguments, start REPL
        print("Tokenizer REPL. Type 'exit' to quit.")
        while True:
            try:
                code = input("> ")
                if code.strip().lower() == "exit":
                    break
                file_reader = FileReader(source_code=code)
                process_code(lexer, file_reader)
            except KeyboardInterrupt:
                print("\nExiting REPL.")
                break

    if error_handler.has_errors():
        print("\nErrors encountered:")
        for error in error_handler.errors:
            print(error)
