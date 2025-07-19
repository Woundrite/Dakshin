class Error(Exception):
    """Base class for all errors."""
    def __init__(self, message, line=None, column=None, file_path=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.file_path = file_path

    def __str__(self):
        location = f"File: {self.file_path}, Line: {self.line}, Column: {self.column}" if self.file_path else ""
        return f"{self.message} {location}".strip()

class SyntaxError(Error):
    """Error for invalid syntax."""
    def __init__(self, message, line, column, file_path):
        super().__init__(f"Syntax Error: {message}", line, column, file_path)

class UnknownTokenError(Error):
    """Error for unknown or invalid tokens."""
    def __init__(self, token, line, column, file_path):
        super().__init__(f"Unknown token '{token}'", line, column, file_path)

class UnterminatedStringError(Error):
    """Error for unterminated string literals."""
    def __init__(self, string, line, column, file_path):
        super().__init__(f"Unterminated string: {string}", line, column, file_path)

class UnterminatedCommentError(SyntaxError):
    def __init__(self, line, column, file_path):
        super().__init__(
            "Unterminated multiline comment", line, column, file_path
        )

class ErrorHandler:
    """Manages and reports errors."""
    def __init__(self):
        self.errors = []

    def report(self, error):
        self.errors.append(error)
        print(error)
        # Don't exit during error reporting - let caller handle it

    def has_errors(self):
        return len(self.errors) > 0

    def clear(self):
        self.errors = []
