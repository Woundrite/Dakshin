# Makefile for Dakshin Assembly Compilation
# Builds 64-bit executables from NASM assembly files

# Compiler and flags
NASM = nasm
GCC = gcc
NASMFLAGS = -f elf64 -g -F dwarf
GCCFLAGS = -m64 -no-pie

# Default target
all: hello

# Compile .dn file to assembly
%.s: %.dn
	python dakshin.py $< $@

# Assemble .s file to object file  
%.o: %.s
	$(NASM) $(NASMFLAGS) $< -o $@

# Link object file to executable
%: %.o
	$(GCC) $(GCCFLAGS) $< -o $@

# Test compilation
hello: tests/sample_programs/simple_io.s
	$(NASM) $(NASMFLAGS) tests/sample_programs/simple_io.s -o simple_io.o
	$(GCC) $(GCCFLAGS) simple_io.o -o simple_io

# Generate assembly from simple_io.dn
tests/sample_programs/simple_io.s: tests/sample_programs/simple_io.dn
	python dakshin.py tests/sample_programs/simple_io.dn tests/sample_programs/simple_io.s

# Clean build artifacts
clean:
	rm -f *.o *.s simple_io tests/sample_programs/*.s tests/sample_programs/*.o

# Test the executable
test: simple_io
	./simple_io

# Help target
help:
	@echo "Dakshin Assembly Build System"
	@echo "=============================="
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build default target (hello)"
	@echo "  hello      - Build simple I/O demo"
	@echo "  test       - Run the compiled executable"
	@echo "  clean      - Remove build artifacts"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Usage:"
	@echo "  make hello              # Compile and link simple_io demo"
	@echo "  make test              # Run the executable"
	@echo "  make %.s SRC=file.dn   # Compile specific .dn file to assembly"
	@echo ""
	@echo "Requirements:"
	@echo "  - NASM (Netwide Assembler)"
	@echo "  - GCC (GNU Compiler Collection)"
	@echo "  - 64-bit Linux system"

.PHONY: all clean test help
