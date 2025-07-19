"""
Standard Library Functions for Dakshin Programming Language
Provides native I/O, string, math, and system functions without imports
"""

class StandardLibrary:
    """Manages built-in functions available in Dakshin"""
    
    def __init__(self):
        self.builtin_functions = {
            # I/O Functions
            'print': {'type': 'io', 'params': ['value'], 'return': 'void'},
            'println': {'type': 'io', 'params': ['value'], 'return': 'void'},
            'input': {'type': 'io', 'params': ['prompt'], 'return': 'string'},
            'printf': {'type': 'io', 'params': ['format', '...'], 'return': 'void'},
            'scanf': {'type': 'io', 'params': ['format', '...'], 'return': 'int'},
            
            # File I/O Functions
            'open': {'type': 'file', 'params': ['filename', 'mode'], 'return': 'file'},
            'close': {'type': 'file', 'params': ['file'], 'return': 'void'},
            'read': {'type': 'file', 'params': ['file'], 'return': 'string'},
            'write': {'type': 'file', 'params': ['file', 'data'], 'return': 'void'},
            'readline': {'type': 'file', 'params': ['file'], 'return': 'string'},
            'writeline': {'type': 'file', 'params': ['file', 'line'], 'return': 'void'},
            'exists': {'type': 'file', 'params': ['filename'], 'return': 'bool'},
            'delete': {'type': 'file', 'params': ['filename'], 'return': 'bool'},
            'copy': {'type': 'file', 'params': ['src', 'dest'], 'return': 'bool'},
            'move': {'type': 'file', 'params': ['src', 'dest'], 'return': 'bool'},
            'size': {'type': 'file', 'params': ['filename'], 'return': 'int'},
            
            # String Functions
            'strlen': {'type': 'string', 'params': ['str'], 'return': 'int'},
            'length': {'type': 'string', 'params': ['str'], 'return': 'int'},  # Alias for strlen
            'strcmp': {'type': 'string', 'params': ['str1', 'str2'], 'return': 'int'},
            'strcpy': {'type': 'string', 'params': ['dest', 'src'], 'return': 'string'},
            'strcat': {'type': 'string', 'params': ['str1', 'str2'], 'return': 'string'},
            'substr': {'type': 'string', 'params': ['str', 'start', 'len'], 'return': 'string'},
            'split': {'type': 'string', 'params': ['str', 'delimiter'], 'return': 'list'},
            'join': {'type': 'string', 'params': ['list', 'separator'], 'return': 'string'},
            'trim': {'type': 'string', 'params': ['str'], 'return': 'string'},
            'upper': {'type': 'string', 'params': ['str'], 'return': 'string'},
            'lower': {'type': 'string', 'params': ['str'], 'return': 'string'},
            'replace': {'type': 'string', 'params': ['str', 'old', 'new'], 'return': 'string'},
            'contains': {'type': 'string', 'params': ['str', 'substr'], 'return': 'bool'},
            'startswith': {'type': 'string', 'params': ['str', 'prefix'], 'return': 'bool'},
            'endswith': {'type': 'string', 'params': ['str', 'suffix'], 'return': 'bool'},
            
            # Math Functions
            'abs': {'type': 'math', 'params': ['value'], 'return': 'number'},
            'min': {'type': 'math', 'params': ['a', 'b'], 'return': 'number'},
            'max': {'type': 'math', 'params': ['a', 'b'], 'return': 'number'},
            'pow': {'type': 'math', 'params': ['base', 'exp'], 'return': 'number'},
            'sqrt': {'type': 'math', 'params': ['value'], 'return': 'float'},
            'floor': {'type': 'math', 'params': ['value'], 'return': 'int'},
            'ceil': {'type': 'math', 'params': ['value'], 'return': 'int'},
            'round': {'type': 'math', 'params': ['value'], 'return': 'int'},
            'sin': {'type': 'math', 'params': ['angle'], 'return': 'float'},
            'cos': {'type': 'math', 'params': ['angle'], 'return': 'float'},
            'tan': {'type': 'math', 'params': ['angle'], 'return': 'float'},
            'log': {'type': 'math', 'params': ['value'], 'return': 'float'},
            'exp': {'type': 'math', 'params': ['value'], 'return': 'float'},
            'random': {'type': 'math', 'params': [], 'return': 'float'},
            'randint': {'type': 'math', 'params': ['min', 'max'], 'return': 'int'},
            
            # Memory Functions
            'malloc': {'type': 'memory', 'params': ['size'], 'return': 'pointer'},
            'free': {'type': 'memory', 'params': ['ptr'], 'return': 'void'},
            'memcpy': {'type': 'memory', 'params': ['dest', 'src', 'size'], 'return': 'pointer'},
            'memset': {'type': 'memory', 'params': ['ptr', 'value', 'size'], 'return': 'pointer'},
            
            # System Functions
            'exit': {'type': 'system', 'params': ['code'], 'return': 'void'},
            'system': {'type': 'system', 'params': ['command'], 'return': 'int'},
            'sleep': {'type': 'system', 'params': ['seconds'], 'return': 'void'},
            'time': {'type': 'system', 'params': [], 'return': 'int'},
            'getenv': {'type': 'system', 'params': ['name'], 'return': 'string'},
            'setenv': {'type': 'system', 'params': ['name', 'value'], 'return': 'bool'},
            
            # Type Conversion Functions
            'tostr': {'type': 'convert', 'params': ['value'], 'return': 'string'},
            'toint': {'type': 'convert', 'params': ['value'], 'return': 'int'},
            'tofloat': {'type': 'convert', 'params': ['value'], 'return': 'float'},
            'tobool': {'type': 'convert', 'params': ['value'], 'return': 'bool'},
            'typeof': {'type': 'convert', 'params': ['value'], 'return': 'string'},
            
            # Collection Functions
            'len': {'type': 'collection', 'params': ['collection'], 'return': 'int'},
            'empty': {'type': 'collection', 'params': ['collection'], 'return': 'bool'},
            'clear': {'type': 'collection', 'params': ['collection'], 'return': 'void'},
            'sort': {'type': 'collection', 'params': ['collection'], 'return': 'void'},
            'reverse': {'type': 'collection', 'params': ['collection'], 'return': 'void'},
            'map': {'type': 'collection', 'params': ['collection', 'function'], 'return': 'list'},
            'filter': {'type': 'collection', 'params': ['collection', 'predicate'], 'return': 'list'},
            'reduce': {'type': 'collection', 'params': ['collection', 'function', 'initial'], 'return': 'any'},
            
            # GUI Functions (Windows API)
            'msgbox': {'type': 'gui', 'params': ['message', 'title'], 'return': 'int'},
            'messagebox': {'type': 'gui', 'params': ['message', 'title', 'type'], 'return': 'int'},
            'inputbox': {'type': 'gui', 'params': ['prompt', 'title'], 'return': 'string'},
            'opendialog': {'type': 'gui', 'params': ['title', 'filter'], 'return': 'string'},
            'savedialog': {'type': 'gui', 'params': ['title', 'filter'], 'return': 'string'},
            'colordialog': {'type': 'gui', 'params': [], 'return': 'int'},
            'fontdialog': {'type': 'gui', 'params': [], 'return': 'string'},
            'folderdialog': {'type': 'gui', 'params': ['title'], 'return': 'string'},
            'showwindow': {'type': 'gui', 'params': ['title', 'width', 'height'], 'return': 'int'},
            'closewindow': {'type': 'gui', 'params': ['window'], 'return': 'void'},
            'getclipboard': {'type': 'gui', 'params': [], 'return': 'string'},
            'setclipboard': {'type': 'gui', 'params': ['text'], 'return': 'void'},
            'beep': {'type': 'gui', 'params': ['frequency', 'duration'], 'return': 'void'},
            'alert': {'type': 'gui', 'params': ['message'], 'return': 'void'},  # Simple alert
            'confirm': {'type': 'gui', 'params': ['message'], 'return': 'bool'},  # Yes/No dialog
            'prompt': {'type': 'gui', 'params': ['message', 'default'], 'return': 'string'},  # Input prompt
        }
    
    def is_builtin(self, function_name):
        """Check if a function is a built-in standard library function"""
        return function_name in self.builtin_functions
    
    def get_function_info(self, function_name):
        """Get information about a built-in function"""
        return self.builtin_functions.get(function_name)
    
    def get_functions_by_type(self, func_type):
        """Get all functions of a specific type"""
        return {name: info for name, info in self.builtin_functions.items() 
                if info['type'] == func_type}
    
    def get_all_functions(self):
        """Get all available built-in functions"""
        return self.builtin_functions.copy()
