# Dakshin Testing Tools

This directory contains various testing utilities and frameworks for the Dakshin programming language.

## Testing Tools

### **Core Testing Utilities**

-   `test_runner.py` - Comprehensive test runner for all .dn files
-   `bug_finder.py` - Focused bug testing and debugging
-   `compile_test.py` - Compilation testing utilities
-   `validate_codegen.py` - Code generation validation

### **Unit Testing Framework**

-   `test_lexer.py` - Lexer unit tests
-   `test_parser.py` - Parser unit tests
-   `test_integration.py` - Integration tests
-   `run_tests.py` - Unit test runner with colored output

## Usage

### Run All Tests

```bash
cd tests/testing_tools
python test_runner.py
```

### Run Unit Tests

```bash
cd tests/testing_tools
python run_tests.py
```

### Run Bug Testing

```bash
cd tests/testing_tools
python bug_finder.py
```

### Validate Code Generation

```bash
cd tests/testing_tools
python validate_codegen.py [test_file.dn]
```

## Test Structure

The testing tools expect the following directory structure:

```
tests/
├── testing_tools/          # This directory
│   ├── test_runner.py      # Main test runner
│   ├── bug_finder.py       # Bug testing
│   └── *.py               # Other testing utilities
├── *.dn                   # Test programs
└── sample_programs/       # Example applications
```

## Development

When adding new testing utilities:

1. Place them in this `testing_tools/` directory
2. Follow the existing patterns for output formatting
3. Update this README with usage instructions
4. Ensure compatibility with the main build system
