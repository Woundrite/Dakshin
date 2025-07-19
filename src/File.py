from Error import Error

class FileReader:
	"""Handles reading the file and tracking position."""
	def __init__(self, file_path=None, source_code=None):
		if file_path:
			self.file_path = file_path
			self.source_code = self._read_file(file_path)
		elif source_code is not None:
			self.file_path = None
			self.source_code = source_code
		else:
			raise ValueError("Either file_path or source_code must be provided.")

		self.pos = 0
		self.line = 1
		self.column = 1

	def _read_file(self, file_path):
		"""Read source code from a file."""
		try:
			with open(file_path, 'r') as file:
				return file.read()
		except FileNotFoundError:
			raise Error(f"File not found: {file_path}")
		except IOError as e:
			raise Error(f"Unable to read file: {e}")

	def current_char(self):
		"""Return the current character or None if at the end."""
		if self.pos < len(self.source_code):
			return self.source_code[self.pos]
		return None

	def advance(self):
		"""Advance to the next character, updating position."""
		if self.pos < len(self.source_code):
			char = self.source_code[self.pos]
			if char == '\n':
				self.line += 1
				self.column = 1
			else:
				self.column += 1
			self.pos += 1

	def get_position(self):
		"""Return the current line and column."""
		return self.line, self.column