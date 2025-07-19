# Dakshin VS Code Extension

This VS Code extension provides comprehensive support for the Dakshin programming language.

## Features

### ✅ **Syntax Highlighting**

-   Full syntax highlighting for `.dn` files
-   Support for keywords, functions, strings, numbers, and comments
-   Custom color themes for Dakshin language constructs

### ✅ **IntelliSense & Autocompletion**

-   Built-in function suggestions (print, println, length, abs, min, max, etc.)
-   Keyword autocompletion
-   Context-aware suggestions

### ✅ **Code Snippets**

-   Quick templates for common patterns:
    -   `main` - Main function template
    -   `func` - Function declaration
    -   `if`/`ifelse` - Conditional statements
    -   `while`/`for` - Loop constructs
    -   `print`/`println` - Output statements
    -   Built-in function snippets

### ✅ **Build Integration**

-   **Compile** (`Ctrl+Shift+B`) - Compile current Dakshin file
-   **Run** (`F5`) - Compile and execute program
-   Auto-compile on save (configurable)
-   Build output in integrated terminal

### ✅ **Project Management**

-   Create new Dakshin projects with templates
-   Proper workspace integration
-   README and project structure generation

### ✅ **Developer Tools**

-   Show AST command for debugging
-   Basic syntax validation
-   Error highlighting and diagnostics

## Installation

### Option 1: Local Development

1. Clone/copy the extension to your VS Code extensions folder
2. Open the extension folder in VS Code
3. Install dependencies: `npm install`
4. Compile: `npm run compile`
5. Press `F5` to launch Extension Development Host

### Option 2: Package and Install

```bash
# Install vsce globally
npm install -g vsce

# Package the extension
cd vscode-extension
vsce package

# Install the .vsix file
code --install-extension dakshin-language-0.1.0.vsix
```

## Configuration

The extension can be configured through VS Code settings:

```json
{
    "dakshin.compiler.path": "python src/compiler.py",
    "dakshin.compiler.outputPath": "./output",
    "dakshin.linting.enabled": true,
    "dakshin.build.autoSave": false
}
```

### Settings Details:

-   **compiler.path**: Path to Dakshin compiler (default: `python src/compiler.py`)
-   **compiler.outputPath**: Directory for compiled output files
-   **linting.enabled**: Enable real-time syntax checking
-   **build.autoSave**: Automatically compile when saving files

## Commands

| Command                       | Shortcut       | Description                  |
| ----------------------------- | -------------- | ---------------------------- |
| `Dakshin: Compile`            | `Ctrl+Shift+B` | Compile current file         |
| `Dakshin: Compile and Run`    | `F5`           | Build and execute            |
| `Dakshin: Create New Project` | -              | Create project template      |
| `Dakshin: Show AST`           | -              | Display Abstract Syntax Tree |

## Language Features

### Supported Constructs:

-   ✅ Functions and procedures
-   ✅ Variables (let, var, const)
-   ✅ Control flow (if/else, while, for)
-   ✅ Built-in functions (I/O, math, string, GUI)
-   ✅ Comments (// and /\* \*/)
-   ✅ String and numeric literals

### Built-in Functions:

-   **I/O**: `print()`, `println()`, `input()`
-   **Math**: `abs()`, `min()`, `max()`, `sqrt()`, `pow()`
-   **String**: `length()`, `strlen()`, `strcmp()`, `strcpy()`
-   **GUI**: `msgbox()`, `alert()`, `confirm()`, `beep()`
-   **System**: `system()`, `time()`, `exit()`

## File Associations

The extension automatically recognizes `.dn` files as Dakshin source code.

## Troubleshooting

### Common Issues:

1. **Compiler not found**

    - Check `dakshin.compiler.path` setting
    - Ensure Python and compiler are in PATH

2. **Build fails**

    - Verify workspace contains Dakshin compiler
    - Check file permissions and paths

3. **Syntax highlighting not working**
    - Ensure file has `.dn` extension
    - Reload VS Code window

## Development

### Project Structure:

```
vscode-extension/
├── package.json              # Extension manifest
├── language-configuration.json # Language config
├── syntaxes/
│   └── dakshin.tmLanguage.json # Syntax grammar
├── snippets/
│   └── dakshin.json           # Code snippets
├── src/
│   └── extension.ts           # Main extension code
└── icons/                     # Extension icons
```

### Building from Source:

```bash
cd vscode-extension
npm install
npm run compile
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## License

This extension is part of the Dakshin programming language project.

## Changelog

### 0.1.0

-   Initial release
-   Basic syntax highlighting
-   Code snippets and autocompletion
-   Build integration
-   Project creation tools
