# Dakshin Compiler Test Suite

This directory contains comprehensive tests for the Dakshin programming language compiler, covering lexical analysis, parsing, and integration testing based on the grammar defined in `grammer.enbf`.

## Test Structure

### Core Test Files

-   **`test_lexer.py`** - Tests for the lexical analyzer (tokenizer)
-   **`test_parser.py`** - Tests for the parser
-   **`test_integration.py`** - End-to-end integration tests
-   **`run_tests.py`** - Test runner script with colored output

### Sample Programs

The `sample_programs/` directory contains example programs that demonstrate various language features:

-   **`comprehensive_demo.dn`** - Comprehensive demonstration of all language features
-   **`calculator.dn`** - Simple calculator implementation
-   **`vehicles.dn`** - Object-oriented programming example with inheritance

## Language Features Tested

Based on the grammar in `grammer.enbf`, the tests cover:

### Lexical Features

-   Keywords and identifiers
-   Numeric literals (integers, floats, binary, hexadecimal)
-   String literals with escape sequences
-   Operators (arithmetic, comparison, logical, bitwise)
-   Delimiters and punctuation
-   Comments (single-line and multi-line)
-   Error handling (unterminated strings, comments)

### Syntactic Features

-   Variable declarations with type annotations
-   Function declarations with parameters and return types
-   Class declarations with inheritance
-   Access modifiers (public, private, protected)
-   Static and abstract members
-   Constructor declarations with super calls
-   Import statements and namespaces
-   Control flow structures:
    -   If-else statements
    -   While and do-while loops
    -   For loops
    -   Switch statements
    -   Match statements with regex patterns
-   Error handling (try-catch-finally)
-   Lambda expressions and function expressions
-   Pointer operations
-   Method calls and member access

### Advanced Features

-   Multiple inheritance
-   Abstract and final classes
-   Override methods
-   Polymorphism
-   Exception handling
-   Regex pattern matching
-   Functional programming constructs

## Running Tests

### Run All Tests

```bash
python tests/run_tests.py
```

### Run Specific Test Suite

```bash
python tests/run_tests.py lexer     # Run only lexer tests
python tests/run_tests.py parser    # Run only parser tests
python tests/run_tests.py integration # Run only integration tests
```

### Run Individual Test Files

```bash
python -m unittest tests.test_lexer
python -m unittest tests.test_parser
python -m unittest tests.test_integration
```

## Test Output

The test runner provides colored output with:

-   ✓ Green checkmarks for passing tests
-   ✗ Red X marks for failing tests
-   -   Dashes for skipped tests
-   Detailed error information for failures
-   Summary statistics with success rate

## Grammar Compliance

All tests are designed to verify compliance with the EBNF grammar defined in `grammer.enbf`. The grammar covers:

```ebnf
program = { import_statement | namespace_declaration | class_declaration | function_declaration } ;

// Core language constructs
import_statement = "import" identifier { "." identifier } [ "as" identifier ] ";"
                 | "from" identifier { "." identifier } "import" identifier_list ";" ;

class_declaration = [ "abstract" | "final" ] "class" identifier [ inheritance_list ]
                   "{" { class_member } "}" ;

function_declaration = [ access_modifier ] [ "static" ] "function" identifier
                      "(" [ parameter_list ] ")" [ "->" type ] block ;

// ... and many more constructs
```

## Test Categories

### Unit Tests

-   **Lexer Tests**: Verify correct tokenization of all language constructs
-   **Parser Tests**: Verify correct parsing and AST generation

### Integration Tests

-   **End-to-End**: Complete compilation pipeline from source to AST
-   **Error Handling**: Proper error detection and reporting
-   **Complex Programs**: Real-world code examples

### Error Tests

-   Syntax error detection
-   Semantic error handling
-   Recovery mechanisms

## Contributing

When adding new language features:

1. Update the grammar in `grammer.enbf`
2. Add corresponding lexer tests in `test_lexer.py`
3. Add parser tests in `test_parser.py`
4. Create integration tests in `test_integration.py`
5. Add sample programs demonstrating the new features
6. Run the full test suite to ensure no regressions

## Test Coverage

The test suite aims for comprehensive coverage of:

-   All grammar productions
-   Edge cases and error conditions
-   Complex nested structures
-   Real-world usage patterns
-   Performance considerations

## Notes

-   Tests use the unittest framework for consistency
-   Mock objects are used to isolate components
-   Error conditions are thoroughly tested
-   Sample programs serve as integration tests and documentation
-   All tests should pass before committing changes
