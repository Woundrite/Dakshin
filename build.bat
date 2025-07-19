@echo off
REM Enhanced Build script for Dakshin Programming Language on Windows
REM Compiles .dn files to executable binaries with GUI support

setlocal enabledelayedexpansion

REM Configuration
set DAKSHIN_COMPILER=python dakshin.py
set NASM=nasm
set LINKER=link
set NASM_FLAGS=-f win64 -g
REM Enhanced linking flags with GUI support and proper library paths
set LINK_FLAGS=/subsystem:console /IGNORE:4210

REM Colors and status messages
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "ERROR=[ERROR]"
set "WARNING=[WARNING]"

REM Exit point to prevent falling through to function definitions
goto :MAIN

REM Functions using labels and goto

:print_status
echo %INFO% %~1
goto :eof

:print_success
echo %SUCCESS% %~1
goto :eof

:print_error
echo %ERROR% %~1
goto :eof

:print_warning
echo %WARNING% %~1
goto :eof

:check_dependencies
call :print_status "Checking dependencies..."

python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python is required but not installed"
    exit /b 1
)

nasm -v >nul 2>&1
if errorlevel 1 (
    call :print_error "NASM is required but not installed"
    call :print_error "Download from: https://www.nasm.us/pub/nasm/releasebuilds/"
    exit /b 1
)

REM Enhanced Visual Studio environment setup
if "%VCINSTALLDIR%"=="" (
    call :print_status "Setting up Visual Studio environment..."
    call :setup_vs_environment
)

REM Check if linker is available
where link >nul 2>&1
if errorlevel 1 (
    call :print_error "Microsoft Link (MSVC) is required but not installed"
    call :print_error "Install Visual Studio or Build Tools for Visual Studio"
    call :print_error "Or run this script from a Visual Studio Developer Command Prompt"
    exit /b 1
)

REM Check for essential libraries
call :check_libraries
if errorlevel 1 (
    call :print_warning "Some libraries may not be found, but will attempt to build anyway"
)

call :print_success "All dependencies found"
goto :eof

:setup_vs_environment
set VS_FOUND=0

REM Try Visual Studio 2022 Community
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
    if not errorlevel 1 set VS_FOUND=1
)

REM Try Visual Studio 2022 Professional
if %VS_FOUND%==0 (
    if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat" (
        call "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
        if not errorlevel 1 set VS_FOUND=1
    )
)

REM Try Visual Studio 2019
if %VS_FOUND%==0 (
    if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" (
        call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
        if not errorlevel 1 set VS_FOUND=1
    )
)

REM Try Build Tools
if %VS_FOUND%==0 (
    if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
        call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
        if not errorlevel 1 set VS_FOUND=1
    )
)

if %VS_FOUND%==0 (
    call :print_warning "Could not automatically setup Visual Studio environment"
    call :print_warning "Please run this script from a Visual Studio Developer Command Prompt"
)
goto :eof

:check_libraries
REM Check for critical libraries in common locations
set LIB_CHECK_PASSED=1

REM Check Windows SDK
if not exist "C:\Program Files (x86)\Windows Kits\10\Lib" (
    if not exist "C:\Program Files\Windows Kits\10\Lib" (
        call :print_warning "Windows SDK not found in standard locations"
        set LIB_CHECK_PASSED=0
    )
)

REM This is just a warning, not a failure
goto :eof

:compile_to_assembly
set source_file=%~1
set asm_file=%~2

call :print_status "Compiling %source_file% to assembly..."

REM Use output file parameter to save assembly directly to file
%DAKSHIN_COMPILER% "%source_file%" "%asm_file%"
if errorlevel 1 (
    call :print_error "Failed to compile %source_file%"
    exit /b 1
)

if not exist "%asm_file%" (
    call :print_error "Assembly file was not created: %asm_file%"
    exit /b 1
)

call :print_success "Assembly generated: %asm_file%"
goto :eof

:assemble_to_object
set asm_file=%~1
set obj_file=%~2

call :print_status "Assembling %asm_file% to object file..."

%NASM% %NASM_FLAGS% "%asm_file%" -o "%obj_file%"
if errorlevel 1 (
    call :print_error "Failed to assemble %asm_file%"
    exit /b 1
)

call :print_success "Object file created: %obj_file%"
goto :eof

:link_executable
set obj_file=%~1
set exe_file=%~2

call :print_status "Linking %obj_file% to executable..."

REM Enhanced linking with GUI support and proper library resolution
REM First try with full paths to common Windows SDK locations
set "LIB_PATHS="
set "LINK_LIBS=kernel32.lib user32.lib ucrt.lib vcruntime.lib legacy_stdio_definitions.lib oldnames.lib libcmt.lib"
set "GUI_LIBS=gdi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib comctl32.lib comdlg32.lib advapi32.lib"

REM Try to find Windows SDK automatically
for /d %%i in ("C:\Program Files (x86)\Windows Kits\10\Lib\*") do (
    if exist "%%i\um\x64\kernel32.lib" (
        set "LIB_PATHS=/LIBPATH:"%%i\um\x64" /LIBPATH:"%%i\ucrt\x64""
        goto found_sdk
    )
)

REM Try Visual Studio 2022 paths
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC" (
    for /d %%i in ("C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\*") do (
        if exist "%%i\lib\x64\legacy_stdio_definitions.lib" (
            set "LIB_PATHS=!LIB_PATHS! /LIBPATH:"%%i\lib\x64""
        )
    )
)

:found_sdk
REM Link with comprehensive library support
%LINKER% %LINK_FLAGS% /entry:main "%obj_file%" /out:"%exe_file%" %LIB_PATHS% %LINK_LIBS% %GUI_LIBS% /NODEFAULTLIB:libucrt.lib
if errorlevel 1 (
    call :print_warning "Standard linking failed, trying alternative approach..."
    
    REM Fallback: Try linking without specific paths (relies on VS environment)
    %LINKER% %LINK_FLAGS% /entry:main "%obj_file%" /out:"%exe_file%" %LINK_LIBS% %GUI_LIBS% /NODEFAULTLIB:libucrt.lib
    if errorlevel 1 (
        call :print_error "Failed to link %obj_file%"
        call :print_error "Please ensure Visual Studio or Windows SDK is properly installed"
        call :print_error "Or run from a Visual Studio Developer Command Prompt"
        exit /b 1
    )
)

for %%F in ("%exe_file%") do set file_size=%%~zF
call :print_success "Executable created: %exe_file%"
call :print_success "File size: !file_size! bytes"
goto :eof

:build_dakshin
set source_file=%~1
set exe_name=%~2

REM Create out directory if it doesn't exist
if not exist "out" mkdir out

REM Derive file names - place intermediate files in out/ directory
for %%F in ("%source_file%") do set base_name=%%~nF
set asm_file=out\%base_name%.asm
set obj_file=out\%base_name%.obj
if "%exe_name%"=="" (
    set exe_file=out\%base_name%.exe
) else (
    set exe_file=out\%exe_name%.exe
)

call :print_status "Building Dakshin program: %source_file%"
call :print_status "Output directory: out\"

REM Step 1: Compile to assembly
call :compile_to_assembly "%source_file%" "%asm_file%"
if errorlevel 1 exit /b 1

REM Step 2: Assemble to object
call :assemble_to_object "%asm_file%" "%obj_file%"
if errorlevel 1 exit /b 1

REM Step 3: Link to executable
call :link_executable "%obj_file%" "%exe_file%"
if errorlevel 1 exit /b 1

REM Cleanup intermediate files
call :print_status "Cleaning up intermediate files..."
del "%asm_file%" "%obj_file%" 2>nul

call :print_success "Build complete! Run with: %exe_file%"
goto :eof

:test_build
call :print_status "Testing Dakshin build system..."

set test_file=tests\sample_programs\simple_io.dn

if not exist "%test_file%" (
    call :print_error "Test file not found: %test_file%"
    exit /b 1
)

call :build_dakshin "%test_file%" "simple_io_test"
if errorlevel 1 exit /b 1

if exist "simple_io_test.exe" (
    call :print_success "Test build successful!"
    call :print_status "Running test executable..."
    simple_io_test.exe
    del simple_io_test.exe 2>nul
) else (
    call :print_error "Test build failed"
    exit /b 1
)
goto :eof

:show_usage
echo Dakshin Build Script for Windows
echo ================================
echo.
echo Usage: %~nx0 [OPTIONS] ^<source.dn^> [executable_name]
echo.
echo Options:
echo   -h, --help      Show this help message
echo   -t, --test      Run test build
echo   -c, --check     Check dependencies only
echo.
echo Examples:
echo   %~nx0 program.dn                    # Build program.dn -^> program.exe
echo   %~nx0 program.dn my_program        # Build program.dn -^> my_program.exe
echo   %~nx0 --test                       # Run test build
echo   %~nx0 --check                      # Check dependencies
echo.
echo Requirements:
echo   - Python 3.x
echo   - NASM (Netwide Assembler)
echo   - Microsoft Visual Studio or Build Tools
echo   - Windows 10/11 64-bit
echo.
echo Technical Details:
echo   - Links with .lib import libraries (not static libraries)
echo   - Runtime dependencies: kernel32.dll, user32.dll, msvcrt.dll
echo   - Uses only C functions (no C++ interference)
echo   - NASM win64 format with Windows x64 calling convention
goto :eof

:MAIN
REM Main script logic
if "%~1"=="-h" goto :show_usage
if "%~1"=="--help" goto :show_usage
if "%~1"=="-t" goto :test_main
if "%~1"=="--test" goto :test_main
if "%~1"=="-c" goto :check_main
if "%~1"=="--check" goto :check_main
if "%~1"=="" goto :no_args

REM Check if first argument starts with -
echo %~1 | findstr /r "^-" >nul
if not errorlevel 1 (
    call :print_error "Unknown option: %~1"
    call :show_usage
    exit /b 1
)

set source_file=%~1
set exe_name=%~2

if not exist "%source_file%" (
    call :print_error "Source file not found: %source_file%"
    exit /b 1
)

call :check_dependencies
if errorlevel 1 exit /b 1

call :build_dakshin "%source_file%" "%exe_name%"
exit /b 0

:test_main
call :check_dependencies
if errorlevel 1 exit /b 1
call :test_build
exit /b 0

:check_main
call :check_dependencies
exit /b 0

:no_args
call :print_error "No source file specified"
call :show_usage
exit /b 1
