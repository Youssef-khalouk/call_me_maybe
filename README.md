*This project has been created as part of the 42 curriculum by ykhalouk.*

# Call Me Maybe

## Description
Call Me Maybe is a function-calling system built on top of a language model. The goal of the project is to demonstrate how constrained decoding can be used to force a model to generate valid function calls instead of arbitrary text.

The program receives a user prompt, analyzes the request, and generates a structured function call when appropriate. By restricting the set of valid tokens during generation, the system ensures that the produced output follows the required format and remains syntactically correct.

The project explores several important concepts related to modern Large Language Models (LLMs), including tokenization, logits, decoding strategies, constrained decoding, and function calling.

## Instructions
- Requires: Python 3.11+
- Install & run:

```bash
make install 
make run
```

## Algorithm (brief)
- Keep a decoding state (JSON keys/values).
- At each token: compute allowed tokens, mask others, then select next token (greedy by default).

## Design decisions
- JSON-first output, explicit state machine, deterministic greedy decode for tests.

## Performance
- Strong syntactic correctness; small CPU overhead per token relative to model inference.

## Challenges
- Tokenization boundary handling and unexpected model text — handled via token mapping and strict masking.

## Testing
- Tests for the tokenizer, state handling, and validator, plus simple tests to make sure the prompt-to-call flow works correctly.

## Example
Input: "What's the weather in Paris?"
Output: `{"function":"get_weather","arguments":{"city":"Paris"}}`

## Resources & AI usage
- References: Transformers, OpenAI function-calling docs, Hugging Face tokenizers, AI.
- AI was used only for explaining how tokenization and AI work, and for answering my questions.
