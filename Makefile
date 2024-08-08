# Make bash the shell
SHELL := /bin/bash
ONESHELL:

ROOT_DIR := $(shell pwd)
SRC_DIR := $(ROOT_DIR)
C_SRC_DIR := $(ROOT_DIR)
C_INCLUDE_DIR := $(ROOT_DIR)/include
C_VENDORS_DIR := $(ROOT_DIR)/vendors
TEST_DIR := $(ROOT_DIR)/tests
COMMAND := $(firstword $(MAKECMDGOALS))
ARGUMENTS := $(filter-out --,$(filter-out $(firstword $(MAKECMDGOALS)),$(MAKECMDGOALS)))
EXECUTABLE := $(firstword $(ARGUMENTS))
FIRST_ARGUMENT := $(word 1, $(ARGUMENTS))
SECOND_ARGUMENT := $(word 2, $(ARGUMENTS))
THIRD_ARGUMENT := $(word 3, $(ARGUMENTS))
EXTRA_ARGS_INDEX := $(shell echo $$(($(words $(filter-out --,$(filter $(ARGUMENTS),--))))))
EXTRA_ARGS := $(wordlist $(shell echo $$(($(EXTRA_ARGS_INDEX) + 2))), $(words $(ARGUMENTS)), $(ARGUMENTS))

TESTING_IN_DOCKER_IMAGE_NAME = testing_in_docker
C_SOURCE_FILES := $(wildcard $(C_SRC_DIR)/**.c)
CLANG_FORMAT := clang-format -i

test-all:
	python -m setup clean && \
	rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && \
	rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && \
	python -m setup build_ext --inplace && python -m pytest . -s -vv


test-leak:
	python -m setup clean && \
	rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && \
	rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && \
	python -m setup build_ext --inplace && pytest --enable-leak-tracking -W error --stacks 10 \
	test_newtype_init.py \
	test_newtype_meth.py \
	test_slots.py \
	test_custom_type.py -vv -s

format:
	@if [ -d $(SRC_DIR)/$(FIRST_ARGUMENT) ]; then \
		ruff format $(SRC_DIR)/$(FIRST_ARGUMENT); \
	elif [ "$(FIRST_ARGUMENT)" == "" ]; then \
		ruff format $(SRC_DIR); \
	else \
		echo "Error: $(FIRST_ARGUMENT) is not a directory."; \
	fi; \
	echo "Formatting C source files now using $(CLANG_FORMAT)"; \
	for file in $(C_SOURCE_FILES); do \
		echo "Formatting $$file now..."; \
		$(CLANG_FORMAT) $$file; \
	done; \
	echo "Formatting is done!";