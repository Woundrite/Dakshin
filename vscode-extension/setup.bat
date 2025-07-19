@echo off
echo ================================
echo Dakshin VS Code Extension Setup
echo ================================

echo.
echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js found

echo.
echo [2/4] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [3/4] Compiling TypeScript...
call npm run compile
if errorlevel 1 (
    echo ERROR: Failed to compile TypeScript
    pause
    exit /b 1
)
echo ✓ TypeScript compiled

echo.
echo [4/4] Installing VSCE (VS Code Extension Manager)...
call npm install -g vsce
if errorlevel 1 (
    echo WARNING: Failed to install vsce globally
    echo You can install it manually with: npm install -g vsce
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To test the extension:
echo 1. Open this folder in VS Code
echo 2. Press F5 to launch Extension Development Host
echo 3. Open a .dn file to test syntax highlighting
echo.
echo To package the extension:
echo 1. Run: vsce package
echo 2. Install the .vsix file: code --install-extension dakshin-language-0.1.0.vsix
echo.
pause
