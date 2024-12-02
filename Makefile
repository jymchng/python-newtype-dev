# Python binary
PYTHON := python

# Poetry
POETRY := poetry

PROJECT_DIR := newtype
SRC := src
EXTENSIONS := extensions

# Docker
DOCKER_DEMO_IMAGE := python-newtype-demo
DOCKERFILE_DEMO_PATH := tests/Dockerfile

DOCKER_TESTS_MULVER_IMAGE := python-newtype-test-mul-vers
DOCKERFILE_TESTS_MULVER_PATH := tests/Dockerfile-test-mul-vers
DOCKER_TAG := latest

# Files and directories
SO_FILES := newtypemethod.cpython-*-linux-gnu.so newtypeinit.cpython-*-linux-gnu.so $(PROJECT_DIR)/$(EXTENSIONS)/newtypemethod.cpython-*-linux-gnu.so $(PROJECT_DIR)/$(EXTENSIONS)/newtypeinit.cpython-*-linux-gnu.so
BUILD_DIR := build
PYTEST_FLAGS := -s -vv

.PHONY: all clean build test test-all test-debug test-custom test-free test-slots test-init test-leak install lint format check venv-poetry clean-deps docker-build docker-run docker-clean docker-demo dist-contents

# Default target
all: clean build test format check venv-poetry clean-deps

# Docker targets
docker-demo-build: build
	docker build -t $(DOCKER_DEMO_IMAGE):$(DOCKER_TAG) -f $(DOCKERFILE_DEMO_PATH) .

docker-demo-run:
	docker run --rm $(DOCKER_DEMO_IMAGE):$(DOCKER_TAG)

docker-demo-clean:
	docker rmi $(DOCKER_DEMO_IMAGE):$(DOCKER_TAG)

# Run complete Docker demo cycle: build, run, clean
docker-demo: docker-demo-build docker-demo-run docker-demo-clean

docker-test-mulvers-build: build
	docker build -t $(DOCKER_TESTS_MULVER_IMAGE):$(DOCKER_TAG) -f $(DOCKERFILE_TESTS_MULVER_PATH) .

docker-test-mulvers-run:
	docker run --rm $(DOCKER_TESTS_MULVER_IMAGE):$(DOCKER_TAG)

docker-test-mulvers-clean:
	docker rmi $(DOCKER_TESTS_MULVER_IMAGE):$(DOCKER_TAG)

# Run complete Docker demo cycle: build, run, clean
docker-test-mulvers: docker-test-mulvers-build docker-test-mulvers-run docker-test-mulvers-clean

# Distribution targets
dist-contents: build
	tar -tzf dist/python_newtype_dev-*.tar.gz

# Check code quality
check:
	ruff check .
	find . -wholename "./newtype/extensions/*.c" -exec cppcheck {} +

# Format code
format:
	ruff format .
	find . -name "*.c" -exec clang-format -i {} +

# Clean build artifacts
clean:
	rm -fr dist
	rm -f $(SO_FILES)
	rm -rf $(BUILD_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-deps:
	pip freeze | xargs pip uninstall -y

# Build extensions
build: clean
	$(POETRY) build

# Build with debug printing enabled
build-debug: clean
	export __PYNT_DEBUG__="true" && make build

# Install dependencies
install: build
	$(PYTHON) -m pip install dist/python_newtype-0.1.0-*.whl

# Run all tests
test:
	$(PYTHON) -m pytest . $(PYTEST_FLAGS)

# Run all tests with debug build
test-debug: build-debug
	$(PYTHON) -m pytest . $(PYTEST_FLAGS) && unset __PYNT_DEBUG__

# Run specific test suites
test-custom:
	$(PYTHON) -m pytest tests/test_custom_type.py $(PYTEST_FLAGS)

test-free:
	$(PYTHON) -m pytest tests/test_freestanding.py $(PYTEST_FLAGS)

test-slots:
	$(PYTHON) -m pytest tests/test_slots.py $(PYTEST_FLAGS)

test-init:
	$(PYTHON) -m pytest tests/test_newtype_init.py $(PYTEST_FLAGS)

test-str:
	$(PYTHON) -m pytest tests/test_newtype_str.py $(PYTEST_FLAGS)

test-async:
	$(PYTHON) -m pytest tests/test_async.py $(PYTEST_FLAGS)

# Run memory leak tests
test-leak:
	$(PYTHON) -m pytest --enable-leak-tracking -W error --stacks 10 tests/test_newtype_init.py $(PYTEST_FLAGS)

# Run a specific test file (usage: make test-file FILE=test_newtype.py)
test-file:
	$(PYTHON) -m pytest $(FILE) $(PYTEST_FLAGS)

# Development workflow targets
dev: clean build test

dev-debug: clean build-debug test

venv-poetry:
	poetry config virtualenvs.in-project true

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
	@echo "  format    	  - Format all codes"
	@echo "  clean-deps   - Uninstall all dependencies in the Virtual Environment"
