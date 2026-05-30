# Makefile for call_me_maybe

PYTHON ?= python
PIP ?= $(PYTHON) -m pip
PACKAGE = .

.PHONY: help install develop run uv-run clean

help:
	@echo "Available targets:"
	@echo "  install   - install package dependencies in editable mode"
	@echo "  develop   - create virtualenv and install editable package"
	@echo "  run       - run the function calling pipeline"
	@echo "  uv-run    - run the pipeline with uv if available"
	@echo "  clean     - remove Python build artifacts"

install:
	$(PIP) install -e $(PACKAGE)

develop:
	python -m venv .venv
	.venv\\Scripts\\activate && $(PIP) install -e $(PACKAGE)

run:
	$(PYTHON) -m call_me_maybe

uv-run:
	uv run $(PYTHON) -m call_me_maybe

clean:
	-rm -rf build dist *.egg-info
