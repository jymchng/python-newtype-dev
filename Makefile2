# Python binary
PYTHON := python

# Files and directories
SO_FILES := newtypemethod.cpython-*-linux-gnu.so newtypeinit.cpython-*-linux-gnu.so
BUILD_DIR := build
PYTEST_FLAGS := -s -vv

.PHONY: all clean build test test-all test-debug test-custom test-free test-slots test-init test-leak install lint

# Default target
all: clean build test

# Clean build artifacts
clean:
	$(PYTHON) -m setup clean --all
	rm -f $(SO_FILES)
	rm -rf $(BUILD_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build extensions
build:
	$(PYTHON) -m setup build_ext --inplace

# Build with debug printing enabled
build-debug:
	$(PYTHON) -m setup build_ext --inplace -D__DEBUG_PRINT__

# Install dependencies
install:
	$(PYTHON) -m pip install -r requirements.txt

# Run all tests
test:
	$(PYTHON) -m pytest . $(PYTEST_FLAGS)

# Run all tests with debug build
test-debug: build-debug
	$(PYTHON) -m pytest . $(PYTEST_FLAGS)

# Run specific test suites
test-custom:
	$(PYTHON) -m pytest test_custom_type.py $(PYTEST_FLAGS)

test-free:
	$(PYTHON) -m pytest test_freestanding.py $(PYTEST_FLAGS)

test-slots:
	$(PYTHON) -m pytest test_slots.py $(PYTEST_FLAGS)

test-init:
	$(PYTHON) -m pytest test_newtype_init.py $(PYTEST_FLAGS)

test-str:
	$(PYTHON) -m pytest test_newtype_str.py $(PYTEST_FLAGS)

test-async:
	$(PYTHON) -m pytest test_async.py $(PYTEST_FLAGS)

# Run memory leak tests
test-leak:
	$(PYTHON) -m pytest --enable-leak-tracking -W error --stacks 10 test_newtype_init.py $(PYTEST_FLAGS)

# Run a specific test file (usage: make test-file FILE=test_newtype.py)
test-file:
	$(PYTHON) -m pytest $(FILE) $(PYTEST_FLAGS)

# Development workflow targets
dev: clean build test

dev-debug: clean build-debug test

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Clean, build, and run tests (default)"
	@echo "  clean        - Remove build artifacts and cache files"
	@echo "  build        - Build C extensions"
	@echo "  build-debug  - Build C extensions with debug printing"
	@echo "  install      - Install project dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-debug   - Run all tests with debug build"
	@echo "  test-custom  - Run custom type tests"
	@echo "  test-free    - Run freestanding tests"
	@echo "  test-slots   - Run slots tests"
	@echo "  test-init    - Run initialization tests"
	@echo "  test-str     - Run string type tests"
	@echo "  test-async   - Run async tests"
	@echo "  test-leak    - Run memory leak tests"
	@echo "  test-file    - Run a specific test file (usage: make test-file FILE=test_newtype.py)"
	@echo "  dev          - Development workflow: clean, build, test"
	@echo "  dev-debug    - Development workflow with debug: clean, build-debug, test"