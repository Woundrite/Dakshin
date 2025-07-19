"""
Assembly Code Generator for Dakshin Programming Language
Converts parsed AST into x86-64 assembly code
"""

import sys
import os

# Add the parent directory to the Python path to import standard_library
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from standard_library import StandardLibrary
except ImportError:
    # Fallback if import fails
    class StandardLibrary:
        def __init__(self):
            self.builtin_functions = {
                'print': {'type': 'io'},
                'println': {'type': 'io'},
                'input': {'type': 'io'},
                'printf': {'type': 'io'},
                'scanf': {'type': 'io'},
            }
        
        def is_builtin(self, function_name):
            return function_name in self.builtin_functions

class AssemblyGenerator:
    def __init__(self):
        self.output = []
        self.data_section = []
        self.text_section = []
        self.string_literals = {}
        self.string_counter = 0
        self.label_counter = 0
        self.lambda_counter = 0  # Counter for unique lambda function names
        self.deferred_lambdas = []  # Store lambda functions to generate later
        self.current_function = None
        self.current_params = []  # Current function parameters
        self.current_locals = {}  # Current function local variables
        self.stack_offset = 0
        self.local_vars = {}
        self.local_var_types = {}  # Track variable types: 'int' or 'string'
        self.stdlib = StandardLibrary()
        
        # Standard I/O buffers
        self.input_buffer_size = 4096
        self.file_descriptors = {}
        self.next_fd = 3  # Start after stdin(0), stdout(1), stderr(2)
        
    def generate(self, ast):
        """Generate assembly code from AST"""
        self.output = []
        self.data_section = []
        self.text_section = []
        
        # Add standard headers
        self.add_headers()
        
        # Process each declaration in the AST
        for declaration in ast:
            self.generate_declaration(declaration)
        
        # Generate deferred lambda functions
        self.generate_deferred_lambdas()
        
        # Combine sections
        result = []
        result.extend(self.data_section)
        result.append("")
        result.extend(self.text_section)
        
        return "\n".join(result)
    
    def add_headers(self):
        """Add standard assembly headers and sections"""
        # Add NASM format and architecture specification for Windows
        self.data_section.extend([
            "; NASM 64-bit assembly for Dakshin Programming Language (Windows)",
            "bits 64",
            "default rel",
            "",
            "section .data",
            "    ; String literals will be placed here",
            "    ; Standard I/O data structures",
            f"    input_buffer times {self.input_buffer_size} db 0",
            "    newline db 13, 10, 0      ; Windows CRLF",
            "    space_string db ' ', 0     ; Space character",
            "    space db 32, 0",
            "    null_terminator db 0",
            "    ; File handling structures",
            "    file_mode_r db 'r', 0",
            "    file_mode_w db 'w', 0",
            "    file_mode_a db 'a', 0",
            "    file_mode_rb db 'rb', 0",
            "    file_mode_wb db 'wb', 0",
            "    ; Format strings for I/O",
            "    fmt_int db '%d', 0",
            "    fmt_float db '%.2f', 0",
            "    fmt_string db '%s', 0",
            "    fmt_char db '%c', 0",
            "    fmt_newline db '%d', 13, 10, 0    ; Windows CRLF",
            "    input_fmt_int db '%d', 0",
            "    input_fmt_float db '%f', 0",
            "    input_fmt_string db '%s', 0",
            "    ; GUI string constants",
            "    alert_title db 'Alert', 0",
            "    confirm_title db 'Confirm', 0", 
            "    error_title db 'Error', 0",
            "    info_title db 'Information', 0"
        ])
        
        self.text_section.extend([
            "",
            "section .text",
            "    ; Entry point for Windows C runtime",
            "    global main",
            "    default rel",
            "",
            "    ; External C runtime functions (Windows)",
            "    extern printf",
            "    extern scanf", 
            "    extern sscanf",
            "    extern fopen",
            "    extern fclose", 
            "    extern fread",
            "    extern fwrite",
            "    extern fgets",
            "    extern fputs",
            "    extern malloc",
            "    extern free",
            "    extern strlen",
            "    extern strcmp",
            "    extern strcpy",
            "    extern strcat",
            "    extern exit",
            "    extern system",
            "    extern _sleep",
            "    extern getenv",
            "    extern _putenv",
            "    extern abs",
            "    extern pow",
            "    extern sqrt",
            "    extern sin",
            "    extern cos",
            "    extern tan",
            "    extern log",
            "    extern exp",
            "    extern rand",
            "    extern srand",
            "    ; GUI Functions (Windows API)",
            "    extern MessageBoxA",
            "    extern Beep",
            "    extern OpenClipboard",
            "    extern CloseClipboard", 
            "    extern GetClipboardData",
            "    extern GlobalLock",
            "    extern GlobalUnlock",
            ""
        ])
        
        # Add standard library function implementations
        self.add_stdlib_functions()
    
    def add_stdlib_functions(self):
        """Add implementations of standard library functions"""
        self.text_section.extend([
            "; === STANDARD I/O FUNCTIONS ===",
            "",
            "; print(value) - Print value to stdout",
            "dakshin_print:",
            "    push rbp",
            "    mov rbp, rsp",
            "    ; Windows x64 calling convention",
            "    sub rsp, 32    ; Shadow space (required for Windows x64)",
            "    ; rcx contains the value to print (Windows convention)",
            "    mov rdx, rcx   ; Move value to second parameter (Windows convention)",
            "    mov rcx, fmt_string  ; Format string in first parameter",
            "    xor rax, rax   ; No vector registers used", 
            "    call printf",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; print_int(value) - Print integer value to stdout",
            "dakshin_print_int:",
            "    push rbp",
            "    mov rbp, rsp",
            "    ; Windows x64 calling convention",
            "    sub rsp, 32    ; Shadow space (required for Windows x64)",
            "    ; rcx contains the integer value to print (Windows convention)",
            "    mov rdx, rcx   ; Move integer to second parameter (Windows convention)",
            "    mov rcx, fmt_int  ; Integer format string in first parameter",
            "    xor rax, rax   ; No vector registers used", 
            "    call printf",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; println(value) - Print value with newline",
            "dakshin_println:",
            "    push rbp", 
            "    mov rbp, rsp",
            "    ; Windows x64 calling convention",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx contains the value to print",
            "    mov rdx, rcx   ; Move value to second parameter",
            "    mov rcx, fmt_string  ; Format string in first parameter",
            "    xor rax, rax   ; No vector registers used",
            "    call printf",
            "    ; Print newline",
            "    mov rcx, newline   ; Newline string in first parameter",
            "    xor rax, rax",
            "    call printf",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; input(prompt) - Read input from stdin",
            "dakshin_input:",
            "    push rbp",
            "    mov rbp, rsp",
            "    ; Windows x64 calling convention",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx contains prompt string",
            "    test rcx, rcx",
            "    jz skip_prompt",
            "    ; Print prompt",
            "    mov rdx, rcx",
            "    mov rcx, fmt_string",
            "    xor rax, rax",
            "    call printf",
            "skip_prompt:",
            "    ; Read input",
            "    mov rcx, input_fmt_string",
            "    mov rdx, input_buffer",
            "    xor rax, rax",
            "    call scanf",
            "    ; Return buffer address",
            "    mov rax, input_buffer",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; === FILE I/O FUNCTIONS ===",
            "",
            "; open(filename, mode) - Open file",
            "dakshin_open:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = filename, rdx = mode",
            "    call fopen",
            "    ; Return file pointer in rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp", 
            "    pop rbp",
            "    ret",
            "",
            "; close(file) - Close file",
            "dakshin_close:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = file pointer",
            "    call fclose",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; read(file) - Read from file",
            "dakshin_read:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 48",  # Shadow space + local vars
            "    ; Save file pointer",
            "    mov [rbp-8], rcx",
            "    ; Allocate buffer for reading",
            "    mov rcx, 4096",
            "    call malloc",
            "    mov [rbp-16], rax    ; Store buffer pointer",
            "    ; Read from file",
            "    mov rcx, rax        ; buffer",
            "    mov rdx, 1          ; size of each element",
            "    mov r8, 4095        ; number of elements",
            "    mov r9, [rbp-8]     ; file pointer",
            "    call fread",
            "    ; Null terminate",
            "    mov rbx, [rbp-16]",
            "    mov byte [rbx+rax], 0",
            "    ; Return buffer",
            "    mov rax, [rbp-16]",
            "    add rsp, 48",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; write(file, data) - Write to file",
            "dakshin_write:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 48    ; Shadow space + local vars",
            "    ; rcx = file, rdx = data",
            "    mov [rbp-8], rcx    ; Save file pointer",
            "    mov [rbp-16], rdx   ; Save data pointer",
            "    mov rcx, rdx        ; data to get length",
            "    call strlen",
            "    mov r8, rax         ; length",
            "    mov rcx, [rbp-16]   ; data",
            "    mov rdx, 1          ; size",
            "    ; r8 already has length",
            "    mov r9, [rbp-8]     ; file",
            "    call fwrite",
            "    add rsp, 48    ; Clean up",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; === STRING FUNCTIONS ===",
            "",
            "; strlen(str) - Get string length",
            "dakshin_strlen:",
            "    push rbp",
            "    mov rbp, rsp",
            "    ; Windows x64 calling convention",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx contains string pointer",
            "    call strlen",
            "    ; Result already in rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; length(str) - Alias for strlen",
            "dakshin_length:",
            "    push rbp",
            "    mov rbp, rsp",
            "    ; Windows x64 calling convention",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx contains string pointer",
            "    call strlen",
            "    ; Result already in rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "    ret",
            "",
            "; strcmp(str1, str2) - Compare strings",
            "dakshin_strcmp:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = str1, rdx = str2 (Windows calling convention)",
            "    call strcmp",
            "    ; Result already in rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; strcpy(dest, src) - Copy string",
            "dakshin_strcpy:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = dest, rdx = src (Windows calling convention)",
            "    call strcpy",
            "    ; Result already in rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; strcat(str1, str2) - Concatenate strings",
            "dakshin_strcat:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = str1, rdx = str2 (Windows calling convention)",
            "    call strcat",
            "    ; Result already in rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; === MATH FUNCTIONS ===",
            "",
            "; abs(value) - Absolute value",
            "dakshin_abs:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx contains value (Windows calling convention)",
            "    mov rax, rcx",
            "    test rax, rax",
            "    jns abs_positive",
            "    neg rax",
            "abs_positive:",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp", 
            "    ret",
            "",
            "; min(a, b) - Minimum of two values",
            "dakshin_min:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = a, rdx = b (Windows calling convention)",
            "    cmp rcx, rdx",
            "    jle min_first",
            "    mov rax, rdx",
            "    jmp min_end",
            "min_first:",
            "    mov rax, rcx",
            "min_end:",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; max(a, b) - Maximum of two values", 
            "dakshin_max:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = a, rdx = b (Windows calling convention)",
            "    cmp rcx, rdx",
            "    jge max_first",
            "    mov rax, rdx",
            "    jmp max_end",
            "max_first:",
            "    mov rax, rcx",
            "max_end:",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; === MEMORY FUNCTIONS ===",
            "",
            "; malloc(size) - Allocate memory",
            "dakshin_malloc:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx contains size (Windows calling convention)",
            "    call malloc",
            "    ; Result already in rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; free(ptr) - Free memory",
            "dakshin_free:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx contains pointer (Windows calling convention)",
            "    call free",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; === SYSTEM FUNCTIONS ===",
            "",
            "; exit(code) - Exit program",
            "dakshin_exit:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space", 
            "    ; rcx contains exit code (Windows calling convention)",
            "    call exit",
            "    ; Should not return",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; system(command) - Execute system command",
            "dakshin_system:",
            "    push rbp",
            "    mov rbp, rsp",
            "    ; Windows calling convention for system()",
            "    sub rsp, 32    ; Shadow space for Windows x64 calling convention",
            "    ; rcx contains command string",
            "    ; rcx already has command - no need to move",
            "    call system",
            "    add rsp, 32    ; Clean up shadow space",
            "    ; Result already in rax",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; time() - Get current time (stub implementation)",
            "dakshin_time:",
            "    push rbp",
            "    mov rbp, rsp",
            "    ; Return a fixed timestamp for now to avoid corruption",
            "    mov rax, 1640995200  ; Fixed timestamp (Jan 1, 2022)",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; === TYPE CONVERSION FUNCTIONS ===",
            "",
            "; toint(str) - Convert string to integer",
            "dakshin_toint:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 48    ; Shadow space + local storage",
            "    ; rcx contains string (Windows calling convention)",
            "    mov rdx, input_fmt_int   ; Format string",
            "    lea r8, [rbp-8]    ; Address for result",
            "    call sscanf",
            "    mov rax, [rbp-8]  ; Get converted value",
            "    add rsp, 48    ; Clean up",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; tofloat(str) - Convert string to float", 
            "dakshin_tofloat:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 48    ; Shadow space + local storage",
            "    ; rcx contains string (Windows calling convention)",
            "    lea rdx, [rbp-8]    ; Address for result",
            "    mov r8, input_fmt_float   ; Format string",
            "    call sscanf",
            "    movq rax, xmm0  ; Get float result",
            "    add rsp, 48    ; Clean up",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; === GUI FUNCTIONS (Windows API) ===",
            "",
            "; msgbox(message, title) - Show message box",
            "dakshin_msgbox:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = message, rdx = title (Windows calling convention)",
            "    mov r9, 0      ; MB_OK type",
            "    mov r8, rdx    ; Title (if provided, otherwise use default)",
            "    test r8, r8",
            "    jnz msgbox_with_title",
            "    mov r8, alert_title  ; Use default title",
            "msgbox_with_title:",
            "    mov rdx, rcx   ; Message",
            "    mov rcx, 0     ; No parent window",
            "    call MessageBoxA",
            "    add rsp, 32    ; Clean up shadow space",
            "    ; Result already in rax",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; alert(message) - Simple alert dialog",
            "dakshin_alert:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = message (Windows calling convention)",
            "    ; Show message box with default title",
            "    mov r9, 0      ; MB_OK type",
            "    mov r8, alert_title  ; Default title",
            "    mov rdx, rcx   ; Message",
            "    mov rcx, 0     ; No parent window",
            "    call MessageBoxA",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; confirm(message) - Yes/No confirmation dialog",
            "dakshin_confirm:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = message (Windows calling convention)",
            "    ; Show Yes/No message box",
            "    mov r9, 4      ; MB_YESNO type",
            "    mov r8, confirm_title  ; Default title",
            "    mov rdx, rcx   ; Message",
            "    mov rcx, 0     ; No parent window",
            "    call MessageBoxA",
            "    ; Convert result: IDYES=6 -> 1, IDNO=7 -> 0",
            "    cmp rax, 6",
            "    sete al        ; Set al to 1 if equal to IDYES",
            "    movzx rax, al  ; Zero extend to rax",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; beep(frequency, duration) - System beep",
            "dakshin_beep:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; rcx = frequency, rdx = duration (Windows calling convention)",
            "    ; If no parameters provided, use defaults",
            "    test rcx, rcx",
            "    jnz beep_with_freq",
            "    mov rcx, 1000  ; Default frequency",
            "beep_with_freq:",
            "    test rdx, rdx",
            "    jnz beep_call",
            "    mov rdx, 500   ; Default duration",
            "beep_call:",
            "    call Beep",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
            "; getclipboard() - Get clipboard text",
            "dakshin_getclipboard:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 32    ; Shadow space",
            "    ; Open clipboard",
            "    mov rcx, 0     ; No window handle",
            "    call OpenClipboard",
            "    test rax, rax",
            "    jz clipboard_error",
            "    ; Get clipboard data",
            "    mov rcx, 1     ; CF_TEXT format",
            "    call GetClipboardData",
            "    mov rbx, rax   ; Save handle",
            "    test rax, rax",
            "    jz close_clipboard",
            "    ; Lock global memory",
            "    mov rcx, rbx",
            "    call GlobalLock",
            "    ; Copy to our buffer (simplified - should allocate proper buffer)",
            "    mov rbx, rax   ; Text pointer",
            "    ; Unlock and close",
            "    mov rcx, rbx",
            "    call GlobalUnlock",
            "close_clipboard:",
            "    call CloseClipboard",
            "    mov rax, rbx   ; Return text pointer",
            "    jmp clipboard_end",
            "clipboard_error:",
            "    mov rax, 0     ; Return null on error",
            "clipboard_end:",
            "    add rsp, 32    ; Clean up shadow space",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            "",
        ])
    
    def generate_declaration(self, node):
        """Generate code for top-level declarations"""
        if node['type'] == 'class':
            self.generate_class(node)
        elif node['type'] == 'function':
            self.generate_function(node)
        elif node['type'] == 'import':
            # Imports are handled at compile time
            pass
        elif node['type'] == 'namespace':
            self.generate_namespace(node)
    
    def generate_class(self, node):
        """Generate assembly for class declarations"""
        class_name = node['name']
        
        # Add class label
        self.text_section.append(f"; Class: {class_name}")
        
        # Generate code for class members
        for member in node['members']:
            if member['type'] == 'constructor':
                self.generate_constructor(member, class_name)
            elif member['type'] == 'function':
                self.generate_method(member, class_name)
    
    def generate_constructor(self, node, class_name):
        """Generate assembly for constructor"""
        constructor_name = f"{class_name}_constructor"
        self.current_function = constructor_name
        self.local_vars = {}
        self.local_var_types = {}
        self.stack_offset = 0
        
        # Function prologue
        self.text_section.extend([
            f"{constructor_name}:",
            "    push rbp",
            "    mov rbp, rsp",
            ""
        ])
        
        # Handle parameters
        params = node.get('params', [])
        for i, param in enumerate(params):
            # Parameters are passed in registers: rcx, rdx, r8, r9 (Windows x64 calling convention)
            register = ['rcx', 'rdx', 'r8', 'r9'][i] if i < 4 else f"[rbp+{16+8*i}]"
            self.local_vars[param['name']] = f"[rbp-{8*(i+1)}]"
            self.text_section.append(f"    mov {self.local_vars[param['name']]}, {register}")
            self.stack_offset += 8
        
        # Handle super call
        if node.get('super'):
            self.text_section.append("    ; Super constructor call")
            # In a real implementation, this would call parent constructor
        
        # Generate constructor body
        if node.get('body'):
            for stmt in node['body']:
                self.generate_statement(stmt)
        
        # Function epilogue
        self.text_section.extend([
            "",
            f"{constructor_name}_end:",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            ""
        ])
    
    def generate_function(self, node):
        """Generate assembly for function declarations"""
        func_name = node['name']
        self.current_function = func_name
        self.local_vars = {}
        self.local_var_types = {}
        self.stack_offset = 0
        
        # Special handling for main function  
        if func_name == 'main':
            # Use C-compatible main function with Windows calling convention
            self.text_section.extend([
                "main:",
                "    push rbp",
                "    mov rbp, rsp",
                "    sub rsp, 128    ; Allocate stack space for local variables + shadow space",
                ""
            ])
        else:
            self.text_section.extend([
                f"{func_name}:",
                "    push rbp",
                "    mov rbp, rsp",
                "    sub rsp, 128    ; Allocate stack space for local variables + shadow space",
                ""
            ])
        
        # Handle parameters (Windows x64 calling convention: RCX, RDX, R8, R9)
        params = node.get('params', [])
        for i, param in enumerate(params):
            register = ['rcx', 'rdx', 'r8', 'r9'][i] if i < 4 else f"[rbp+{32+8*i}]"  # Windows uses 4 registers
            self.local_vars[param['name']] = f"[rbp-{8*(i+1)}]"
            # Force parameter type to int for now (we'll implement proper type inference later)
            self.local_var_types[param['name']] = 'int'
            self.text_section.append(f"    mov {self.local_vars[param['name']]}, {register}")
            self.stack_offset += 8
        
        # Generate function body
        if node.get('body'):
            for stmt in node['body']:
                self.generate_statement(stmt)
        
        # Function epilogue
        if func_name == 'main':
            self.text_section.extend([
                "",
                f"{func_name}_end:",
                "    ; Restore stack and return to C runtime (Windows x64)",
                "    mov rsp, rbp",  # This automatically cleans up all allocated space
                "    pop rbp", 
                "    ret",
                ""
            ])
        else:
            self.text_section.extend([
                "",
                f"{func_name}_end:",
                "    mov rsp, rbp",  # This automatically cleans up all allocated space
                "    pop rbp",
                "    ret",
                ""
            ])
    
    def generate_method(self, node, class_name):
        """Generate assembly for class methods"""
        method_name = f"{class_name}_{node['name']}"
        self.generate_function({**node, 'name': method_name})
    
    def generate_namespace(self, node):
        """Generate code for namespace declarations"""
        # Process namespace body
        for declaration in node['body']:
            self.generate_declaration(declaration)
    
    def generate_statement(self, node):
        """Generate assembly for statements"""
        if node['type'] == 'expr_stmt':
            self.generate_expression(node['expr'])
        elif node['type'] == 'return':
            if node.get('value'):
                # Evaluate return expression into rax
                self.generate_expression(node['value'])
            self.text_section.extend([
                f"    jmp {self.current_function}_end"
            ])
        elif node['type'] == 'variable_declaration':
            self.generate_variable_declaration(node)
        elif node['type'] == 'let':
            self.generate_variable_declaration(node)
        elif node['type'] == 'var_decl':
            self.generate_variable_declaration(node)
        elif node['type'] == 'assignment':
            self.generate_assignment(node)
        elif node['type'] == 'if':
            self.generate_if_statement(node)
        elif node['type'] == 'while':
            self.generate_while_statement(node)
        elif node['type'] == 'for':
            self.generate_for_statement(node)
        elif node['type'] == 'switch':
            self.generate_switch_statement(node)
        elif node['type'] == 'try':
            self.generate_try_statement(node)
        elif node['type'] == 'break':
            self.generate_break_statement(node)
        elif node['type'] == 'continue':
            self.generate_continue_statement(node)
        elif node['type'] == 'block':
            # Handle block statements
            body = node.get('body', node.get('statements', []))
            for stmt in body:
                self.generate_statement(stmt)
        else:
            # Unknown statement type - add comment
            self.text_section.append(f"    ; Unknown statement type: {node['type']}")
    
    def generate_expression(self, node):
        """Generate assembly for expressions"""
        if node['type'] == 'call':
            self.generate_function_call(node)
        elif node['type'] == 'assignment':
            self.generate_assignment(node)
        elif node['type'] == 'identifier':
            self.generate_identifier(node)
        elif node['type'] == 'string':
            self.generate_string_literal(node)
        elif node['type'] == 'number':
            self.generate_number_literal(node)
        elif node['type'] == 'binary':
            self.generate_binary_operation(node)
        elif node['type'] == 'unary':
            self.generate_unary_operation(node)
        elif node['type'] == 'member':
            self.generate_member_access(node)
        elif node['type'] == 'new':
            self.generate_new_expression(node)
        elif node['type'] == 'cast':
            self.generate_cast_expression(node)
        elif node['type'] == 'instanceof':
            self.generate_instanceof_expression(node)
        elif node['type'] == 'lambda':
            self.generate_lambda_expression(node)
    
    def generate_function_call(self, node):
        """Generate assembly for function calls"""
        callee = node['callee']
        args = node.get('args', [])
        
        # Get function name
        if callee['type'] == 'identifier':
            func_name = callee['value']
        elif callee['type'] == 'member':
            func_name = f"{callee['object']['value']}.{callee['member']}"
        else:
            func_name = 'unknown'
        
        # Handle built-in standard library functions
        if self.stdlib.is_builtin(func_name):
            self.generate_stdlib_call(func_name, args)
        else:
            # General function call
            self.generate_general_call(func_name, args)
    
    def generate_stdlib_call(self, func_name, args):
        """Generate assembly for standard library function calls"""
        # Save caller-saved registers
        self.text_section.append("    ; Save caller-saved registers")
        
        # Handle different standard library functions
        if func_name == 'print':
            self.generate_print_call(args)
        elif func_name == 'println':
            self.generate_println_call(args)
        elif func_name == 'input':
            self.generate_input_call(args)
        elif func_name == 'printf':
            self.generate_printf_call(args)
        elif func_name == 'scanf':
            self.generate_scanf_call(args)
        elif func_name in ['open', 'close', 'read', 'write', 'readline', 'writeline']:
            self.generate_file_io_call(func_name, args)
        elif func_name in ['strlen', 'length', 'strcmp', 'strcpy', 'strcat', 'substr', 'trim', 'upper', 'lower']:
            self.generate_string_call(func_name, args)
        elif func_name in ['abs', 'min', 'max', 'pow', 'sqrt', 'sin', 'cos', 'tan', 'log', 'exp']:
            self.generate_math_call(func_name, args)
        elif func_name in ['malloc', 'free', 'memcpy', 'memset']:
            self.generate_memory_call(func_name, args)
        elif func_name in ['exit', 'system', 'sleep', 'time', 'getenv', 'setenv']:
            self.generate_system_call(func_name, args)
        elif func_name in ['toint', 'tofloat', 'tostr', 'tobool', 'typeof']:
            self.generate_conversion_call(func_name, args)
        elif func_name in ['len', 'empty', 'clear', 'sort', 'reverse']:
            self.generate_collection_call(func_name, args)
        else:
            # Fallback to general call
            self.generate_general_call(func_name, args)
    
    def generate_general_call(self, func_name, args):
        """Generate assembly for general function calls (Windows x64 calling convention)"""
        # Save caller-saved registers and align stack
        # Note: We don't save rax since it will contain the return value
        self.text_section.extend([
            "    ; Save caller-saved registers (Windows x64)",
            "    push rcx", 
            "    push rdx",
            "    push r8",
            "    push r9",
            "    push r10",
            "    push r11"
        ])
        
        # Windows x64 requires 32 bytes of shadow space
        self.text_section.append("    sub rsp, 32    ; Shadow space")
        
        # Ensure 16-byte stack alignment
        stack_args = max(0, len(args) - 4)  # Windows uses 4 registers
        if (stack_args % 2) == 1:
            self.text_section.append("    sub rsp, 8    ; Align stack")
        
        # Evaluate arguments and place in registers/stack (Windows x64 convention)
        # Windows x64: RCX, RDX, R8, R9 for first 4 integer parameters
        for i, arg in enumerate(args):
            if i < 4:
                # Use registers for first 4 arguments (Windows convention)
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
            else:
                # Use stack for additional arguments (in reverse order)
                self.generate_expression(arg)
                self.text_section.append("    push rax")
        
        # Check if this is a lambda function call (function pointer in a variable)
        if func_name in self.local_vars or func_name in self.current_locals:
            # Indirect call through function pointer
            if func_name in self.local_vars:
                var_location = self.local_vars[func_name]
            else:
                var_location = self.current_locals[func_name]
            
            self.text_section.extend([
                f"    mov rax, {var_location}  ; Load function pointer",
                f"    call rax                ; Indirect call"
            ])
        else:
            # Direct call to named function
            self.text_section.extend([
                f"    call {func_name}",
                "    ; Function result in rax"
            ])
        
        # Clean up stack if needed
        if len(args) > 4:
            stack_cleanup = (len(args) - 4) * 8
            self.text_section.append(f"    add rsp, {stack_cleanup}")
        
        # Restore alignment if needed
        if (stack_args % 2) == 1:
            self.text_section.append("    add rsp, 8    ; Restore alignment")
        
        # Clean up shadow space
        self.text_section.append("    add rsp, 32    ; Clean up shadow space")
        
        # Restore caller-saved registers
        self.text_section.extend([
            "    pop r11",
            "    pop r10", 
            "    pop r9",
            "    pop r8",
            "    pop rdx",
            "    pop rcx",
            "    ; rax contains return value"
        ])
    
    def generate_print_call(self, args):
        """Generate assembly for print function calls"""
        if args:
            arg = args[0]  # Print first argument
            if arg['type'] == 'string':
                # Create string literal
                string_label = self.create_string_literal(arg['value'])
                
                self.text_section.extend([
                    f"    ; Print string: {arg['value']}",
                    f"    mov rcx, {string_label}",
                    "    call dakshin_print"
                ])
            elif arg['type'] == 'number':
                # Print number
                self.generate_expression(arg)
                self.text_section.extend([
                    f"    mov rcx, rax    ; Number to print",
                    "    call dakshin_print"
                ])
            else:
                # Evaluate expression and print result
                self.generate_expression(arg)
                self.text_section.extend([
                    f"    mov rcx, rax    ; Result to print",
                    "    call dakshin_print"
                ])
    
    def generate_println_call(self, args):
        """Generate assembly for println function calls"""
        if args:
            # For multiple arguments, print each one separated by a space
            for i, arg in enumerate(args):
                if i > 0:
                    # Print a space between arguments
                    self.text_section.extend([
                        "    mov rcx, space_string",
                        "    call dakshin_print"
                    ])
                
                # Check if this argument should be printed as an integer
                should_print_as_int = False
                
                # Case 1: Function call that returns an integer
                if (arg['type'] == 'call' and 
                    arg['callee']['type'] == 'identifier' and 
                    arg['callee']['value'] in ['length', 'strlen', 'time', 'abs', 'min', 'max', 'toint']):
                    should_print_as_int = True
                
                # Case 2: Variable that contains an integer
                elif (arg['type'] == 'identifier' and 
                      arg['value'] in self.local_var_types and 
                      self.local_var_types[arg['value']] == 'int'):
                    should_print_as_int = True
                
                # Case 3: Binary expressions (arithmetic and comparison operations result in integers)
                elif (arg['type'] == 'binary' and 
                      arg['op'] in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=']):
                    should_print_as_int = True
                
                # Case 4: Number literals
                elif arg['type'] == 'number':
                    should_print_as_int = True
                
                if should_print_as_int:
                    # Generate the expression for this integer argument
                    self.generate_expression(arg)
                    self.text_section.extend([
                        "    mov rcx, rax",
                        "    call dakshin_print_int"
                    ])
                else:
                    # Generate the expression for this argument (string or other)
                    self.generate_expression(arg)
                    self.text_section.extend([
                        "    mov rcx, rax",
                        "    call dakshin_print"
                    ])
            
            # Print newline at the end
            self.text_section.extend([
                "    mov rcx, newline",
                "    call dakshin_print"
            ])
        else:
            # No arguments, just print newline
            self.text_section.extend([
                "    mov rcx, newline",
                "    call dakshin_print"
            ])
    
    def generate_input_call(self, args):
        """Generate assembly for input function calls"""
        if args:
            # With prompt
            self.generate_expression(args[0])
            self.text_section.extend([
                "    mov rcx, rax    ; Prompt string",
                "    call dakshin_input"
            ])
        else:
            # No prompt
            self.text_section.extend([
                "    mov rcx, 0      ; No prompt",
                "    call dakshin_input"
            ])
    
    def generate_printf_call(self, args):
        """Generate assembly for printf function calls"""
        if args:
            # Format string
            self.generate_expression(args[0])
            self.text_section.append("    mov rcx, rax")
            
            # Additional arguments
            for i, arg in enumerate(args[1:], 1):
                if i < 4:
                    register = ['rdx', 'r8', 'r9'][i-1]
                    self.generate_expression(arg)
                    self.text_section.append(f"    mov {register}, rax")
                else:
                    self.generate_expression(arg)
                    self.text_section.append("    push rax")
            
            self.text_section.extend([
                "    xor rax, rax      ; No floating point args",
                "    call printf"
            ])
    
    def generate_file_io_call(self, func_name, args):
        """Generate assembly for file I/O function calls"""
        # Prepare arguments
        for i, arg in enumerate(args):
            if i < 4:
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
        
        # Call the appropriate function
        self.text_section.append(f"    call dakshin_{func_name}")
    
    def generate_string_call(self, func_name, args):
        """Generate assembly for string function calls"""
        # Windows x64 calling convention: rcx, rdx, r8, r9
        for i, arg in enumerate(args):
            if i < 4:
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
        
        # Call the appropriate function
        if func_name == 'length':
            # length is an alias for strlen
            self.text_section.append(f"    call dakshin_strlen")
        else:
            self.text_section.append(f"    call dakshin_{func_name}")
    
    def generate_math_call(self, func_name, args):
        """Generate assembly for math function calls"""
        # Windows x64 calling convention: rcx, rdx, r8, r9
        for i, arg in enumerate(args):
            if i < 4:
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
        
        # Call the appropriate function
        self.text_section.append(f"    call dakshin_{func_name}")
    
    def generate_memory_call(self, func_name, args):
        """Generate assembly for memory function calls"""
        # Windows x64 calling convention: rcx, rdx, r8, r9
        for i, arg in enumerate(args):
            if i < 4:
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
        
        # Call the appropriate function
        self.text_section.append(f"    call dakshin_{func_name}")
    
    def generate_system_call(self, func_name, args):
        """Generate assembly for system function calls"""
        # Windows x64 calling convention: rcx, rdx, r8, r9
        for i, arg in enumerate(args):
            if i < 4:
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
        
        # Call the appropriate function
        self.text_section.append(f"    call dakshin_{func_name}")
    
    def generate_conversion_call(self, func_name, args):
        """Generate assembly for type conversion function calls"""
        if args:
            self.generate_expression(args[0])
            self.text_section.extend([
                "    mov rcx, rax",
                f"    call dakshin_{func_name}"
            ])
    
    def generate_collection_call(self, func_name, args):
        """Generate assembly for collection function calls"""
        # Windows x64 calling convention: rcx, rdx, r8, r9
        for i, arg in enumerate(args):
            if i < 4:
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
        
        # Call the appropriate function (these would need implementation)
        self.text_section.append(f"    call dakshin_{func_name}")
    
    def generate_identifier(self, node):
        """Generate assembly for identifier access"""
        var_name = node['value']
        if var_name in self.local_vars:
            # Load the VALUE from the variable location, not the address
            var_location = self.local_vars[var_name]
            # var_location is already formatted as [rbp-offset], so we can use it directly
            self.text_section.append(f"    mov rax, {var_location}")
        elif var_name in self.current_locals:
            # Lambda parameter or local variable
            var_location = self.current_locals[var_name]
            self.text_section.append(f"    mov rax, {var_location}")
        else:
            # Global variable or parameter
            self.text_section.append(f"    mov rax, {var_name}")
    
    def generate_string_literal(self, node):
        """Generate assembly for string literals"""
        string_label = self.create_string_literal(node['value'])
        self.text_section.append(f"    mov rax, {string_label}")
    
    def generate_number_literal(self, node):
        """Generate assembly for number literals"""
        value = node['value']
        self.text_section.append(f"    mov rax, {value}")
    
    def generate_binary_operation(self, node):
        """Generate assembly for binary operations"""
        op = node['op']
        left = node['left']
        right = node['right']
        
        # Handle instanceof specially - don't evaluate right side as expression
        if op == 'instanceof':
            self.generate_instanceof_check(left, right)
            return
        
        # Evaluate left operand
        self.generate_expression(left)
        self.text_section.append("    push rax    ; Save left operand")
        
        # Evaluate right operand
        self.generate_expression(right)
        self.text_section.append("    mov rbx, rax    ; Right operand in rbx")
        self.text_section.append("    pop rax         ; Left operand in rax")
        
        # Perform operation
        if op == '+':
            self.text_section.append("    add rax, rbx")
        elif op == '-':
            self.text_section.append("    sub rax, rbx")
        elif op == '*':
            self.text_section.append("    imul rax, rbx")
        elif op == '/':
            self.text_section.extend([
                "    cqo             ; Sign extend rax to rdx:rax",
                "    idiv rbx        ; Divide rdx:rax by rbx"
            ])
        elif op == '==':
            label = self.get_next_label()
            self.text_section.extend([
                "    cmp rax, rbx",
                f"    sete al         ; Set al to 1 if equal",
                "    movzx rax, al   ; Zero extend to rax"
            ])
        elif op == '!=':
            self.text_section.extend([
                "    cmp rax, rbx",
                "    setne al        ; Set al to 1 if not equal",
                "    movzx rax, al   ; Zero extend to rax"
            ])
        elif op == '<':
            self.text_section.extend([
                "    cmp rax, rbx",
                "    setl al         ; Set al to 1 if less",
                "    movzx rax, al   ; Zero extend to rax"
            ])
        elif op == '>':
            self.text_section.extend([
                "    cmp rax, rbx",
                "    setg al         ; Set al to 1 if greater",
                "    movzx rax, al   ; Zero extend to rax"
            ])
        elif op == '<=':
            self.text_section.extend([
                "    cmp rax, rbx",
                "    setle al        ; Set al to 1 if less or equal",
                "    movzx rax, al   ; Zero extend to rax"
            ])
        elif op == '>=':
            self.text_section.extend([
                "    cmp rax, rbx",
                "    setge al        ; Set al to 1 if greater or equal",
                "    movzx rax, al   ; Zero extend to rax"
            ])
        else:
            # Unknown operator
            self.text_section.append(f"    ; Unknown binary operator: {op}")
            self.text_section.append("    mov rax, 0  ; Default to 0")
    
    def generate_unary_operation(self, node):
        """Generate assembly for unary operations"""
        op = node['op']
        operand = node['right']
        
        self.generate_expression(operand)
        
        if op == '-':
            self.text_section.append("    neg rax")
        elif op == '!':
            self.text_section.extend([
                "    test rax, rax",
                "    setz al         ; Set al to 1 if rax is 0",
                "    movzx rax, al   ; Zero extend to rax"
            ])
    
    def generate_variable_declaration(self, node):
        """Generate assembly for variable declarations"""
        var_name = node['name']
        var_type = node.get('var_type')
        
        # Allocate space on stack
        self.stack_offset += 8
        self.local_vars[var_name] = f"[rbp-{self.stack_offset}]"
        
        # Handle dynamic variables
        if var_type == "dynamic":
            self.local_var_types[var_name] = 'dynamic'
            # Initialize dynamic variables to null/zero
            self.text_section.append(f"    mov qword {self.local_vars[var_name]}, 0  ; Initialize dynamic variable")
            return
        
        # Initialize if there's an initial value (use 'value' field from AST)
        init_value = node.get('init', node.get('value'))
        if init_value:
            # Determine variable type based on initial value
            if init_value['type'] == 'number':
                self.local_var_types[var_name] = 'int'
            elif init_value['type'] == 'string':
                self.local_var_types[var_name] = 'string'
            elif init_value['type'] == 'binary':
                # Binary operations on numbers result in numbers
                self.local_var_types[var_name] = 'int'
            elif (init_value['type'] == 'call' and 
                  init_value['callee']['type'] == 'identifier' and 
                  init_value['callee']['value'] in ['length', 'strlen', 'time', 'abs', 'min', 'max', 'toint']):
                # Integer-returning function calls
                self.local_var_types[var_name] = 'int'
            elif init_value['type'] == 'call':
                # For now, assume all user-defined function calls return integers
                self.local_var_types[var_name] = 'int'
            else:
                # Default to string for unknown types
                self.local_var_types[var_name] = 'string'
            
            self.generate_expression(init_value)
            self.text_section.append(f"    mov {self.local_vars[var_name]}, rax")
        else:
            # No initial value, default to int
            self.local_var_types[var_name] = 'int'
    
    def generate_assignment(self, node):
        """Generate assembly for variable assignments"""
        var_name = node['name']
        
        # Check if variable exists
        if var_name not in self.local_vars:
            # Variable doesn't exist, treat as new variable declaration
            self.stack_offset += 8
            self.local_vars[var_name] = f"[rbp-{self.stack_offset}]"
            self.local_var_types[var_name] = 'int'  # Default to int for assignments
        
        # Generate expression for the new value
        value_expr = node['value']
        
        # Update variable type based on assignment value (especially for dynamic variables)
        current_type = self.local_var_types.get(var_name, 'int')
        
        if value_expr['type'] == 'number':
            new_type = 'int'
        elif value_expr['type'] == 'string':
            new_type = 'string'
        elif value_expr['type'] == 'binary' and value_expr['op'] in ['+', '-', '*', '/', '%']:
            new_type = 'int'
        elif (value_expr['type'] == 'call' and 
              value_expr['callee']['type'] == 'identifier' and 
              value_expr['callee']['value'] in ['length', 'strlen', 'time', 'abs', 'min', 'max', 'toint']):
            new_type = 'int'
        elif value_expr['type'] == 'call':
            # For now, assume all function calls return integers (we'll implement proper type inference later)
            new_type = 'int'
        else:
            # For identifier references, preserve existing type unless it's dynamic
            new_type = current_type if current_type != 'dynamic' else 'int'
        
        # Allow type changes for dynamic variables
        if current_type == 'dynamic' or current_type != new_type:
            self.local_var_types[var_name] = new_type
            self.text_section.append(f"    ; Variable '{var_name}' type: {current_type} -> {new_type}")
        
        self.generate_expression(value_expr)
        self.text_section.append(f"    mov {self.local_vars[var_name]}, rax")
    
    def generate_if_statement(self, node):
        """Generate assembly for if statements"""
        else_label = self.get_next_label("else")
        end_label = self.get_next_label("end_if")
        
        # Evaluate condition (use 'cond' field from AST)
        condition = node.get('cond', node.get('condition'))
        if condition:
            self.generate_expression(condition)
            self.text_section.extend([
                "    test rax, rax",
                f"    jz {else_label}"
            ])
        else:
            # If no condition, treat as always true
            self.text_section.append(f"    ; No condition found in if statement")
        
        # Generate then block
        if node.get('then'):
            self.generate_statement(node['then'])
        self.text_section.append(f"    jmp {end_label}")
        
        # Generate else block
        self.text_section.append(f"{else_label}:")
        if node.get('else'):
            self.generate_statement(node['else'])
        
        self.text_section.append(f"{end_label}:")
    
    def generate_while_statement(self, node):
        """Generate assembly for while loops"""
        start_label = self.get_next_label("while_start")
        end_label = self.get_next_label("while_end")
        
        self.text_section.append(f"{start_label}:")
        
        # Evaluate condition
        condition = node.get('cond', node.get('condition'))
        if condition:
            self.generate_expression(condition)
            self.text_section.extend([
                "    test rax, rax",
                f"    jz {end_label}"
            ])
        
        # Generate body
        self.generate_statement(node['body'])
        self.text_section.append(f"    jmp {start_label}")
        
        self.text_section.append(f"{end_label}:")
    
    def generate_for_statement(self, node):
        """Generate assembly for for loops"""
        start_label = self.get_next_label("for_start")
        end_label = self.get_next_label("for_end")
        continue_label = self.get_next_label("for_continue")
        
        # Generate initialization
        if node.get('init'):
            self.generate_statement(node['init'])
        
        self.text_section.append(f"{start_label}:")
        
        # Evaluate condition
        if node.get('condition'):
            self.generate_expression(node['condition'])
            self.text_section.extend([
                "    test rax, rax",
                f"    jz {end_label}"
            ])
        
        # Generate body
        if node.get('body'):
            self.generate_statement(node['body'])
        
        # Generate increment
        self.text_section.append(f"{continue_label}:")
        if node.get('update'):
            self.generate_expression(node['update'])
        elif node.get('increment'):
            self.generate_expression(node['increment'])
        
        self.text_section.append(f"    jmp {start_label}")
        self.text_section.append(f"{end_label}:")
    
    def generate_switch_statement(self, node):
        """Generate assembly for switch statements"""
        end_label = self.get_next_label("switch_end")
        
        # Evaluate switch expression
        self.generate_expression(node['expr'])
        self.text_section.append("    push rax    ; Save switch value")
        
        # Generate cases
        for case in node.get('cases', []):
            case_label = self.get_next_label("case")
            self.text_section.append(f"{case_label}:")
            
            # Compare case value
            self.text_section.append("    pop rax     ; Restore switch value")
            self.text_section.append("    push rax    ; Keep switch value")
            self.generate_expression(case['value'])
            self.text_section.extend([
                "    mov rbx, rax",
                "    pop rax",
                "    push rax",
                "    cmp rax, rbx",
                f"    jne {self.get_next_label('next_case')}"
            ])
            
            # Generate case body
            for stmt in case['statements']:
                self.generate_statement(stmt)
        
        # Generate default case
        if node.get('default'):
            default_label = self.get_next_label("default")
            self.text_section.append(f"{default_label}:")
            for stmt in node['default']:
                self.generate_statement(stmt)
        
        self.text_section.append("    pop rax     ; Clean up switch value")
        self.text_section.append(f"{end_label}:")
    
    def generate_try_statement(self, node):
        """Generate assembly for try-catch statements"""
        catch_label = self.get_next_label("catch")
        end_label = self.get_next_label("try_end")
        
        # Generate try block
        self.text_section.append("    ; Try block")
        if node.get('try'):
            self.generate_statement(node['try'])
        
        self.text_section.append(f"    jmp {end_label}")
        
        # Generate catch block
        self.text_section.append(f"{catch_label}:")
        if node.get('catch'):
            self.generate_statement(node['catch'])
        
        self.text_section.append(f"{end_label}:")
    
    def generate_break_statement(self, node):
        """Generate assembly for break statements"""
        # In a real implementation, this would jump to the end of the current loop
        self.text_section.append("    ; Break statement - simplified")
    
    def generate_continue_statement(self, node):
        """Generate assembly for continue statements"""
        # In a real implementation, this would jump to the loop condition
        self.text_section.append("    ; Continue statement - simplified")
    
    def generate_member_access(self, node):
        """Generate assembly for member access"""
        # Simplified: assume member access is field access
        object_expr = node['object']
        member_name = node['member']
        
        self.generate_expression(object_expr)
        # In a real implementation, this would calculate offset
        self.text_section.append(f"    ; Member access: {member_name}")
    
    def generate_new_expression(self, node):
        """Generate assembly for object creation"""
        class_name = node['class']
        args = node.get('args', [])
        
        self.text_section.extend([
            f"    ; Create new {class_name}",
            "    ; Allocate memory (simplified)",
            "    mov rax, 64     ; Assume 64 bytes per object",
            "    ; Call malloc or allocate on heap"
        ])
        
        # Call constructor
        if args:
            # Set up arguments for constructor call
            for i, arg in enumerate(args[:4]):
                register = ['rcx', 'rdx', 'r8', 'r9'][i]
                self.generate_expression(arg)
                self.text_section.append(f"    mov {register}, rax")
        
        self.text_section.append(f"    call {class_name}_constructor")
    
    def generate_cast_expression(self, node):
        """Generate assembly for type casting"""
        expr = node['expr']
        target_type = node['target_type']
        
        # Generate expression
        self.generate_expression(expr)
        
        # Type casting is mostly a no-op in assembly
        self.text_section.append(f"    ; Cast to {target_type}")
    
    def generate_instanceof_expression(self, node):
        """Generate assembly for instanceof checks (deprecated - using binary operation handler)"""
        left = node['left']
        right = node['right']
        self.generate_instanceof_check(left, right)
    
    def generate_instanceof_check(self, left_expr, right_expr):
        """Generate assembly for instanceof type checking"""
        # Get the variable name from left expression
        if left_expr['type'] == 'identifier':
            var_name = left_expr['value']
        else:
            # For complex expressions, evaluate and use result
            self.text_section.append("    ; Complex instanceof left expression")
            self.generate_expression(left_expr)
            var_name = None
        
        # Get the type name from right expression
        if right_expr['type'] == 'identifier':
            type_name = right_expr['value']
        else:
            self.text_section.append("    ; Error: instanceof requires type identifier on right")
            self.text_section.append("    mov rax, 0  ; Default to false")
            return
        
        self.text_section.append(f"    ; instanceof check: {var_name} instanceof {type_name}")
        
        # Check if variable is dynamic and handle type checking
        if var_name and var_name in self.local_var_types:
            current_type = self.local_var_types[var_name]
            
            self.text_section.append(f"    ; Variable '{var_name}' has type: {current_type}")
            
            if current_type == 'dynamic':
                # For dynamic variables, check runtime type tracking
                self.text_section.extend([
                    f"    ; Dynamic instanceof check for {var_name}",
                    f"    mov rax, {self.local_vars[var_name]}  ; Load variable value"
                ])
                
                # For dynamic variables, use simplified runtime type checking
                # In a real implementation, we'd have type metadata stored with each value
                if type_name.lower() in ['int', 'integer']:
                    self.text_section.extend([
                        "    ; Check if dynamic value represents integer",
                        "    ; In full implementation, would check type tag",
                        "    mov rax, 1  ; Simplified: assume dynamic int check passes"
                    ])
                elif type_name.lower() in ['string', 'str']:
                    self.text_section.extend([
                        "    ; Check if dynamic value represents string",
                        "    ; In full implementation, would check string type tag",
                        "    mov rax, 1  ; Simplified: assume dynamic string check passes"
                    ])
                else:
                    self.text_section.extend([
                        f"    ; Check if dynamic value is instance of {type_name}",
                        "    mov rax, 1  ; Simplified: assume custom type check passes"
                    ])
            else:
                # For statically typed variables, direct type comparison
                self.text_section.append(f"    ; Static type check: {current_type} instanceof {type_name}")
                
                # Direct string comparison of types
                if current_type.lower() == type_name.lower():
                    self.text_section.append("    mov rax, 1  ; Type matches")
                else:
                    # Check inheritance/compatibility
                    compatible = self.check_type_compatibility(current_type, type_name)
                    self.text_section.append(f"    mov rax, {1 if compatible else 0}  ; Type {'compatible' if compatible else 'incompatible'}")
        else:
            # Variable not found - attempt to check the left expression result
            if var_name:
                self.text_section.extend([
                    f"    ; Variable {var_name} not found in scope",
                    "    mov rax, 0  ; Default to false for unknown variables"
                ])
            else:
                # Complex expression - evaluate it and do basic type checking
                self.text_section.extend([
                    f"    ; instanceof check for expression result",
                    "    mov rax, 0  ; Default to false for complex expressions"
                ])
    
    def check_type_compatibility(self, current_type, target_type):
        """Check if current_type is compatible with target_type (inheritance)"""
        # Basic type compatibility rules
        if current_type == target_type:
            return True
        
        # Case-insensitive comparison
        if current_type.lower() == target_type.lower():
            return True
        
        # Inheritance checking would go here
        # For now, simplified compatibility rules
        if target_type.lower() == 'any':
            return True
        
        # Number type compatibility
        if current_type in ['int', 'float', 'double'] and target_type.lower() in ['number', 'numeric']:
            return True
        
        return False
    
    def generate_lambda_expression(self, node):
        """Generate assembly for lambda expressions"""
        params = node.get('params', [])
        body = node['body']
        
        # Generate unique lambda function name
        lambda_name = f"lambda_{self.lambda_counter}"
        self.lambda_counter += 1
        
        # Store lambda for deferred generation
        self.deferred_lambdas.append({
            'name': lambda_name,
            'params': params,
            'body': body
        })
        
        # Return lambda function address in current context
        self.text_section.extend([
            f"    ; Load lambda function address",
            f"    mov rax, {lambda_name}"
        ])
    
    def generate_deferred_lambdas(self):
        """Generate all deferred lambda functions at the end"""
        for lambda_info in self.deferred_lambdas:
            self.generate_lambda_function(lambda_info)
    
    def generate_lambda_function(self, lambda_info):
        """Generate assembly for a lambda function"""
        lambda_name = lambda_info['name']
        params = lambda_info['params']
        body = lambda_info['body']
        
        # Save current context
        current_function = self.current_function
        current_params = self.current_params
        current_locals = self.current_locals
        
        # Set up lambda context
        self.current_function = lambda_name
        self.current_params = params.copy()
        self.current_locals = {}
        
        # Generate lambda function
        param_count = len(params)
        self.text_section.extend([
            f"; Lambda function: {lambda_name}",
            f"{lambda_name}:",
            "    push rbp",
            "    mov rbp, rsp",
            f"    sub rsp, {max(32, param_count * 8 + 32)}    ; Allocate stack space for locals + shadow space"
        ])
        
        # Set up parameter access
        for i, param in enumerate(params):
            if i == 0:
                self.text_section.append(f"    mov [rbp-{(i+1)*8}], rcx    ; Parameter {param}")
                self.current_locals[param] = f"[rbp-{(i+1)*8}]"
            elif i == 1:
                self.text_section.append(f"    mov [rbp-{(i+1)*8}], rdx    ; Parameter {param}")
                self.current_locals[param] = f"[rbp-{(i+1)*8}]"
            elif i == 2:
                self.text_section.append(f"    mov [rbp-{(i+1)*8}], r8     ; Parameter {param}")
                self.current_locals[param] = f"[rbp-{(i+1)*8}]"
            elif i == 3:
                self.text_section.append(f"    mov [rbp-{(i+1)*8}], r9     ; Parameter {param}")
                self.current_locals[param] = f"[rbp-{(i+1)*8}]"
            else:
                # Additional parameters are on the stack
                stack_offset = 16 + (i - 4) * 8
                self.text_section.append(f"    mov rax, [rbp+{stack_offset}]")
                self.text_section.append(f"    mov [rbp-{(i+1)*8}], rax    ; Parameter {param}")
                self.current_locals[param] = f"[rbp-{(i+1)*8}]"
        
        # Generate lambda body
        if isinstance(body, list):
            # Multi-line lambda with block (body is a list of statements)
            for stmt in body:
                self.generate_statement(stmt)
        else:
            # Single expression lambda - generate expression and return its value
            self.generate_expression(body)
            # Expression result is in rax - no need to move it
        
        # Function epilogue
        self.text_section.extend([
            f"{lambda_name}_end:",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
            ""
        ])
        
        # Restore previous context
        self.current_function = current_function
        self.current_params = current_params
        self.current_locals = current_locals
    
    def create_string_literal(self, string_value):
        """Create a string literal in the data section"""
        # Remove quotes and handle escape sequences
        clean_string = string_value.strip('"').replace('\\n', '", 10, "').replace('\\"', '"')
        
        if string_value not in self.string_literals:
            label = f"str_{self.string_counter}"
            self.string_literals[string_value] = label
            self.string_counter += 1
            
            # Add to data section
            self.data_section.append(f'    {label} db "{clean_string}", 0')
        
        return self.string_literals[string_value]
    
    def get_next_label(self, prefix="label"):
        """Generate unique labels"""
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label


def main():
    """Test the assembly generator with the constructor example"""
    # Sample AST from test_constructor.dn
    ast = [
        {
            "type": "class",
            "name": "TestClass",
            "base": [],
            "modifiers": [],
            "members": [
                {
                    "type": "constructor",
                    "name": "TestClass",
                    "params": [
                        {
                            "name": "param",
                            "type": "int"
                        }
                    ],
                    "modifiers": ["public"],
                    "super": {"args": []},
                    "body": [
                        {
                            "type": "expr_stmt",
                            "expr": {
                                "type": "call",
                                "callee": {
                                    "type": "identifier",
                                    "value": "print"
                                },
                                "args": [
                                    {
                                        "type": "string",
                                        "value": '"Constructor called"'
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    ]
    
    # Generate assembly
    generator = AssemblyGenerator()
    assembly_code = generator.generate(ast)
    
    print("Generated Assembly Code:")
    print("=" * 50)
    print(assembly_code)


if __name__ == "__main__":
    main()
