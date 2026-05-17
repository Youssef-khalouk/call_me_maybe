from llm_sdk import Small_LLM_Model
import numpy as np
import json


model = Small_LLM_Model()

file_content = ""
with open("data/input/functions_definition.json", "r") as file:
    file_content = file.readlines()

input = f'Functions:{file_content}\nQuestion: What is the sum of 2 and 3?\nAnswer: ' + '{"function": "'

response = ""

while True:
    tokens = model.encode(input)
    tokens_array = tokens[0].tolist()

    predictions = model.get_logits_from_input_ids(tokens_array)

    next_token = np.argmax(predictions)

    word = model.decode(next_token)

    if '"' in word:
        break

    input += word

    response += word

    print(word, end = "", flush=True)


input = f'Functions:{file_content}\nQuestion: What is the sum of 2 and 3?\nAnswer: ' + '{"function": "' + response + '", "parameters": {"'

parameters = '{"'

while True:
    tokens = model.encode(input)
    tokens_array = tokens[0].tolist()

    predictions = model.get_logits_from_input_ids(tokens_array)

    next_token = np.argmax(predictions)

    word = model.decode(next_token)


    if '}' in word:
        parameters += "}"
        break

    parameters += word

    input += word

    print(word, end = "", flush=True)


print("\n\n")

print(response)

print(parameters)