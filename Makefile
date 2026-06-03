.PHONY: help install run debug clean lint lint-strict

parameters =    --functions_definition data/input/functions_definition.json \
				--input data/input/function_calling_tests.json \
				--output data/output/function_calls.json

help:
	@echo "Available targets:"
	@echo "  make install      Install project dependencies"
	@echo "  make run          Run the application"
	@echo "  make debug        Run the application with pdb"
	@echo "  make clean        Remove cache and temporary files"
	@echo "  make lint         Run flake8 and mypy with required flags"
	@echo "  make lint-strict  Run flake8 and mypy --strict"

install:
	pip install flake8
	pip install mypy
	uv sync

run:
	uv run python -m  src $(parameters)

debug:
	uv run python -m pdb src $(parameters)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 src
	mypy src    --warn-return-any \
	            --warn-unused-ignores \
	            --ignore-missing-imports \
	            --disallow-untyped-defs \
	            --check-untyped-defs
