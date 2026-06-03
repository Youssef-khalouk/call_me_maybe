*This project has been created as part of the 42 curriculum by ykhalouk.*

# Call Me Maybe

## Description

Call Me Maybe is a function-calling system built on top of a language model. The goal of the project is to demonstrate how constrained decoding can be used to force a model to generate valid function calls instead of arbitrary text.

The program receives a user prompt, analyzes the request, and generates a structured function call when appropriate. By restricting the set of valid tokens during generation, the system ensures that the produced output follows the required format and remains syntactically correct.

The project explores several important concepts related to modern Large Language Models (LLMs), including tokenization, logits, decoding strategies, constrained decoding, and function calling.

## Features

* Custom tokenizer and vocabulary handling
* Custom decoding implementation
* Constrained decoding
* Function-call generation
* Structured JSON output
* Validation of generated function calls
* Command-line interface

---

## Instructions

### Requirements

* Python 3.11+
* uv (recommended)

### Installation

```bash
make install
```

or manually:

```bash
uv sync
```

### Running

```bash
make run
```

or:

```bash
uv run python main.py
```

### Debugging

```bash
make debug
```

### Linting

```bash
make lint
```

### Strict Linting

```bash
make lint-strict
```

### Cleaning

```bash
make clean
```

---

## Algorithm Explanation

### Constrained Decoding

The core of the project is a constrained decoding algorithm.

Normally, an LLM predicts a probability distribution over the entire vocabulary. During decoding, the token with the highest probability (or a sampled token) is selected.

In this project, decoding is restricted according to the current generation state.

Example:

If the model is generating:

```json
{
  "function":
```

only valid tokens that can legally follow this position are allowed.

The algorithm performs the following steps:

1. Obtain logits from the model.
2. Determine the current decoding state.
3. Build a list of valid next tokens.
4. Mask all invalid tokens.
5. Select the highest-scoring valid token.
6. Append the token to the output.
7. Repeat until completion.

This guarantees that generated outputs always satisfy the expected grammar.

### Token Masking

Invalid tokens are assigned negative infinity:

```python
logits[token_id] = -float("inf")
```

As a result, the decoder can never select them.

### State Tracking

The decoder maintains information about:

* Current JSON nesting level
* Current object key
* Current function being generated
* Allowed parameter names
* End-of-generation conditions

This information determines which tokens are valid at each step.

---

## Design Decisions

### Custom Decoder

A custom decoder was implemented instead of using an existing framework.

Reasons:

* Better understanding of LLM internals
* Full control over token selection
* Easier experimentation
* Educational value

### Deterministic Generation

The project primarily uses greedy decoding:

```python
next_token = argmax(valid_logits)
```

Benefits:

* Reproducible results
* Easier debugging
* Predictable behavior

### JSON-Based Function Calls

JSON was selected because:

* Human-readable
* Easy to validate
* Common industry format
* Compatible with most APIs

---

## Performance Analysis

### Accuracy

The constrained decoder guarantees syntactically valid outputs.

Without constraints:

* Invalid JSON may be generated.
* Function names may be misspelled.
* Required arguments may be omitted.

With constraints:

* Only valid structures are produced.
* Function names remain valid.
* Output format is guaranteed.

### Speed

Constrained decoding introduces additional overhead because valid-token sets must be computed at each generation step.

However, for the scale of this project, the overhead remains small and does not significantly impact user experience.

### Reliability

Reliability is improved because invalid outputs are prevented before generation rather than corrected afterward.

---

## Challenges Faced

### Tokenization

Handling unknown words and token boundaries required careful design.

Solution:

* Vocabulary lookup
* Longest-match token search
* Fallback mechanisms

### Constrained Generation

Determining which tokens should be valid at each state was initially difficult.

Solution:

* Explicit state machine
* Rule-based validation
* Incremental testing

### JSON Validation

Maintaining correct nesting and structure during generation was challenging.

Solution:

* Context tracking
* Grammar constraints
* Structured output rules

---

## Testing Strategy

Several testing approaches were used.

### Unit Tests

Individual components were tested:

* Tokenizer
* Encoder
* Decoder
* Constraint engine

### Integration Tests

End-to-end tests were performed:

```text
Prompt -> Encoding -> Model -> Decoding -> Function Call
```

### Edge Cases

Special attention was given to:

* Empty prompts
* Unknown words
* Invalid function names
* Missing arguments
* Deeply nested structures

### Manual Testing

Various prompts were entered manually to verify correctness and consistency.

---

## Example Usage

### Example 1

Input:

```text
What's the weather in Paris?
```

Output:

```json
{
  "function": "get_weather",
  "arguments": {
    "city": "Paris"
  }
}
```

### Example 2

Input:

```text
Send an email to Alice
```

Output:

```json
{
  "function": "send_email",
  "arguments": {
    "recipient": "Alice"
  }
}
```

### Example 3

Run the application:

```bash
make run
```

Debug:

```bash
make debug
```

Lint:

```bash
make lint
```

---

## Resources

### Documentation

* Python Documentation
* NumPy Documentation
* mypy Documentation
* flake8 Documentation

### Learning Resources

* Attention Is All You Need
* OpenAI Function Calling Documentation
* Hugging Face Documentation
* Tokenization and Decoding Tutorials

### AI Usage

AI tools were used as learning assistants during the development of the project.

Tasks where AI was used:

* Understanding constrained decoding concepts
* Reviewing implementation ideas
* Explaining tokenizer behavior
* Clarifying LLM terminology
* Assisting with debugging discussions

All implementation decisions, coding, testing, and final validation were performed manually.
