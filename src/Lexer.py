import re
from File import FileReader
from Error import SyntaxError, UnknownTokenError, UnterminatedCommentError, UnterminatedStringError, ErrorHandler
from Tokens import TokenType, Token

class Lexer:
	def __init__(self, error_handler):
		self.error_handler = error_handler
		self.TOKEN_SPECIFICATION = [
			# Comments (must come before division)
			(TokenType.MULTILINE_COMMENT_START, r'/\*'),  # Start of multiline comment
			(TokenType.MULTILINE_COMMENT_END, r'\*/'),    # End of multiline comment
			(TokenType.COMMENT, r'//.*'),           # Single-line comments
			
			# String literals
			(TokenType.STRING, r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''),
			(TokenType.UNTERMINATED_STRING, r'"([^"\\]|\\.)*$|\'([^\']|\\.)*$'),
			
			# Regex literals
			(TokenType.REGEX, r'/(?:[^/\n\\]|\\.)+/'),  # Regex patterns like /pattern/
			
			# Numeric literals
			(TokenType.BINARY, r'0b[01]+'),         # Binary numbers (e.g., 0b101)
			(TokenType.HEX, r'0x[0-9A-Fa-f]+'),     # Hexadecimal numbers (e.g., 0x1A3)
			(TokenType.FLOAT, r'\d+\.\d+'),         # Floating-point numbers
			(TokenType.INTEGER, r'\d+'),            # Integers
			
			# Multi-character operators (must come before single character ones)
			(TokenType.EXPONENT, r'\*\*'),          # Exponentiation operator
			(TokenType.SHIFT_LEFT, r'<<'),          # Left shift operator
			(TokenType.SHIFT_RIGHT, r'>>'),         # Right shift operator
			(TokenType.EQUAL, r'=='),               # Equality operator
			(TokenType.NEQUAL, r'!='),              # Not equal operator
			(TokenType.LTE, r'<='),                 # Less than or equal to operator
			(TokenType.GTE, r'>='),                 # Greater than or equal to operator
			(TokenType.AND, r'&&'),                 # Logical AND
			(TokenType.OR, r'\|\|'),                # Logical OR
			
			# Single-character operators
			(TokenType.PLUS, r'\+'),                # Plus operator
			(TokenType.FUNCTION_ARROW, r'->'),      # Function arrow (must come before MINUS)
			(TokenType.MINUS, r'-'),                # Minus operator
			(TokenType.MUL, r'\*'),                 # Multiplication operator
			(TokenType.DIV, r'/'),                  # Division operator
			(TokenType.MOD, r'%'),                  # Modulo operator
			(TokenType.ARROW, r'=>'),               # Arrow operator (must come before ASSIGN)
			(TokenType.ASSIGN, r'='),               # Assignment operator
			(TokenType.LT, r'<'),                   # Less than operator
			(TokenType.GT, r'>'),                   # Greater than operator
			(TokenType.NOT, r'!'),                  # Logical NOT
			(TokenType.BITWISE_AND, r'&'),          # Bitwise AND
			(TokenType.BITWISE_OR, r'\|'),          # Bitwise OR
			(TokenType.BITWISE_XOR, r'\^'),         # Bitwise XOR
			
			# Delimiters
			(TokenType.LPAREN, r'\('),              # Left parenthesis
			(TokenType.RPAREN, r'\)'),              # Right parenthesis
			(TokenType.LBRACKET, r'\['),            # Left bracket
			(TokenType.RBRACKET, r'\]'),            # Right bracket
			(TokenType.LBRACE, r'\{'),              # Left brace
			(TokenType.RBRACE, r'\}'),              # Right brace
			(TokenType.DOT, r'\.'),                 # Dot
			(TokenType.COLON, r':'),                # Colon
			(TokenType.SEMICOLON, r';'),            # Semicolon
			(TokenType.COMMA, r','),                # Comma
			
			# Identifiers
			(TokenType.IDENT, r'[A-Za-z_]\w*'),     # Identifiers
			
			# Whitespace and newlines
			(TokenType.NEWLINE, r'\n'),             # Line breaks
			(TokenType.WHITESPACE, r'[ \t]+'),      # Spaces and tabs
			
			# Catch-all for unknown characters
			(TokenType.UNKNOWN, r'.'),              # Catch-all for unknown characters
		]
		self.get_token = re.compile('|'.join(
			f'(?P<{name.value}>{pattern})' for name, pattern in self.TOKEN_SPECIFICATION
		)).match
	def skip_multiline_comment(self, file_reader, start_line, start_column):
		"""Skips characters until the end of a multiline comment or reports an error if it's unterminated."""
		while True:
			char = file_reader.current_char()
			if char is None:
				# End of file reached without finding `*/`
				self.error_handler.report(
					UnterminatedCommentError(start_line, start_column, file_reader.file_path)
				)
				return False
			elif char == '*':
				# Check for the end of the comment
				file_reader.advance()  # Consume '*'
				if file_reader.current_char() == '/':
					file_reader.advance()  # Consume '/'
					return True
			else:
				file_reader.advance()  # Move to the next character
	
	def tokenize(self, file_reader):
		"""Tokenize input from a FileReader."""
		tokens = []
		while (char := file_reader.current_char()) is not None:

			match = self.get_token(file_reader.source_code, file_reader.pos)
			if not match:
				# If no token matches, we have an unknown token
				line, column = file_reader.get_position()
				self.error_handler.report(
					UnknownTokenError(file_reader.source_code[file_reader.pos], line, column, file_reader.file_path)
				)
				# Skip the problematic character and move ahead by 1 position
				file_reader.pos += 1
				continue

			token_type_name = match.lastgroup  # Get the matched group name
			token_type = TokenType[token_type_name]  # Use the Enum to get the token type
			value = match.group()

			if token_type == TokenType.WHITESPACE:
				# Skip whitespace and advance the position
				file_reader.pos = match.end()
				continue
			elif token_type == TokenType.MULTILINE_COMMENT_START:
				# Handle multiline comments
				file_reader.pos = match.end()  # Move past the start delimiter
				start_line, start_column = file_reader.get_position()
				if not self.skip_multiline_comment(file_reader, start_line, start_column):
					# Unterminated comment error is reported inside skip_multiline_comment
					break
			elif token_type == TokenType.STRING:
				# For valid strings, add them as tokens
				# tokens.append((token_type, value))
				tokens.append(Token(token_type, value))
				file_reader.pos = match.end()  # Move past the string token
			elif token_type == TokenType.UNTERMINATED_STRING:
				# Handle unterminated strings and report the error
				line, column = file_reader.get_position()
				self.error_handler.report(
					UnterminatedStringError(value, line, column, file_reader.file_path)
				)
				# Move past the unterminated string (skip to the next character)
				file_reader.pos = match.end()  # Advancing past the unterminated string
			elif token_type == TokenType.COMMENT:
				# If we encounter a comment, just skip it and move to the next line
				file_reader.pos = match.end()  # Move past the comment
				continue  # Skip adding comments as tokens
			elif token_type == TokenType.INTEGER:
				# For integers, add them as tokens
				# tokens.append((token_type, int(value)))
				tokens.append(Token(token_type, int(value)))
				file_reader.pos = match.end()
			elif token_type == TokenType.FLOAT:
				# For floats, add them as tokens
				# tokens.append((token_type, float(value)))
				tokens.append(Token(token_type, float(value)))
				file_reader.pos = match.end()
			elif token_type == TokenType.BINARY:
				# For binary numbers, add them as tokens
				# tokens.append((token_type, int(value, 2)))
				tokens.append(Token(token_type, int(value, 2)))
				file_reader.pos = match.end()
			elif token_type == TokenType.HEX:
				# For hexadecimal numbers, add them as tokens
				# tokens.append((token_type, int(value, 16)))
				tokens.append(Token(token_type, int(value, 16)))
				file_reader.pos = match.end()
			else:
				# For all other valid tokens, add to the list
				# tokens.append((token_type, value))
				tokens.append(Token(token_type, value))
				# Move past the matched token
				file_reader.pos = match.end()

		return tokens
