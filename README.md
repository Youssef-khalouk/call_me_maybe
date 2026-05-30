# call_me_maybe

A local LLM inference toolkit for experimenting with function calling and prompt-driven output generation using a Hugging Face causal language model.

## Overview

This repository contains:

- `llm_sdk/` — a lightweight local SDK for loading and running a Hugging Face causal language model.
- `call_me_maybe/` — a small application layer that:
  - loads function definitions and user prompts from JSON files,
  - uses a local model to predict which function should be called,
  - extracts function arguments token-by-token,
  - writes the results to an output JSON file.
- `data/` — sample input and output data for testing the function calling flow.

## Key Components

- `llm_sdk/__init__.py`
  - `Small_LLM_Model` wraps a Hugging Face causal LM, tokenization, and logits extraction.
- `call_me_maybe/get_data.py`
  - `GetData` loads functions and prompts from JSON files and provides helper accessors.
- `call_me_maybe/my_model.py`
  - `My_Model` wraps `Small_LLM_Model` with a simple tokenizer/decoder and next-token utilities.
- `call_me_maybe/__main__.py`
  - CLI entry point that runs the function calling pipeline from JSON input to JSON output.
- `call_me_maybe/main.py`
  - A simple Tkinter UI demo for interacting with the model in a chat-like manner.

## Requirements

- Python 3.10+
- `torch>=2.0.0`
- `transformers>=4.40.0`
- `huggingface-hub>=0.20.0`

## Install

```bash
python -m pip install -e .
```

If you prefer a clean environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -e .
```

## Usage

### Run the function calling pipeline

```bash
python -m call_me_maybe
```

If you use `uv`, the equivalent command is:

```bash
uv run python -m call_me_maybe
```

By default, the script uses:

- `data/input/functions_definition.json`
- `data/input/function_calling_tests.json`
- `data/output/function_calls.json`

Custom paths can be provided:

```bash
python -m call_me_maybe --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```

### Run the UI demo

```bash
python call_me_maybe/main.py
```

This launches a small Tkinter window for interactive model prompting.

## Data Format

- `functions_definition.json` should contain a list of function definitions with names and parameter schemas.
- `function_calling_tests.json` should contain a list of prompt objects, each with a `prompt` field.
- Output is written as a list of selected function calls with `prompt`, `name`, and `parameters`.

## Notes

- The `llm_sdk` package downloads tokenizer files from the Hugging Face Hub and loads a local causal language model.
- `call_me_maybe/__main__.py` implements a custom token decoding loop for function selection and parameter extraction.
- The current code is optimized for experimentation rather than production.

## License

Add your preferred license here.
