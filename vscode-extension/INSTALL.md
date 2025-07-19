# Quick Installation Guide for Dakshin VS Code Extension

## 🚀 Easy Installation

### Step 1: Install Dependencies

```bash
cd vscode-extension
npm install
```

### Step 2: Compile Extension

```bash
npx tsc
```

### Step 3: Test in Development Mode

1. Open VS Code
2. File → Open Folder → Select `vscode-extension` directory
3. Press `F5` to launch Extension Development Host
4. Open any `.dn` file (like `Programs\hello_world.dn`)

### Step 4: Install Permanently (Optional)

```bash
# Install vsce if not already installed
npm install -g @vscode/vsce

# Package the extension
npx vsce package

# Install the .vsix file
code --install-extension dakshin-language-0.1.0.vsix
```

## 🎯 Testing the Extension

1. Open `Programs\hello_world.dn` in VS Code
2. You should see:
    - ✨ **Syntax Highlighting**: Keywords like `function`, `return` in color
    - 🔤 **Function Names**: `main`, `print` highlighted differently
    - 🎨 **Strings**: `"Hello world"` in string color
    - 💡 **IntelliSense**: Type `pr` and see `print()` suggestion

## 🛠️ Available Commands

After installation, use `Ctrl+Shift+P` and type:

-   `Dakshin: Compile` - Compile current file
-   `Dakshin: Run` - Compile and run current file
-   `Dakshin: Create New Project` - Create new Dakshin project

## 📝 Code Snippets

Type these in a `.dn` file:

-   `main` + Tab → Main function template
-   `func` + Tab → Function template
-   `if` + Tab → If-else template
-   `for` + Tab → For loop template
-   `while` + Tab → While loop template

## ✅ Features Working

✅ Syntax highlighting for all Dakshin keywords  
✅ IntelliSense for all 87 built-in functions  
✅ Code snippets for common patterns  
✅ Build integration with compile/run commands  
✅ Error detection and highlighting  
✅ File association for `.dn` files

## 🔧 Troubleshooting

**If extension doesn't load:**

1. Make sure `out/extension.js` exists after compilation
2. Check VS Code Developer Tools (`Help` → `Toggle Developer Tools`) for errors
3. Restart VS Code after installation

**If syntax highlighting doesn't work:**

1. Ensure file has `.dn` extension
2. Check `View` → `Command Palette` → `Change Language Mode` → Select "Dakshin"

**If IntelliSense doesn't work:**

1. Make sure TypeScript compiled without errors
2. Check that `package.json` has correct activation events
3. Try reloading VS Code window (`Ctrl+Shift+P` → `Developer: Reload Window`)
