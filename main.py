from llm_sdk import Small_LLM_Model
import numpy as np
import json

model = Small_LLM_Model()

vocab_path = model.get_path_to_vocab_file()
tokenizer_path = model.get_path_to_tokenizer_file()


with open(vocab_path, "r", encoding="utf-8") as file:
    vocab_dict = json.loads(file.read())

def split(prompt):
    tokens = []
    word = ""
    for i, ch in enumerate(prompt):
        if ch == " ":
            if word != "":
                tokens.append(word)
                word = " "
        else:
            word += ch
        if i == len(prompt) - 1 and word != "":
            tokens.append(word)
    for i in range(len(tokens)):
        word = list(tokens[i])
        for x in range(len(word)):
            if word[x] == " ":
                word[x] = "Ġ"
        tokens[i] = "".join(word)
    return tokens

def encode_word(word):
    tokens = []
    start = 0

    while start < len(word):
        found = False
        for end in range(len(word), start, -1):
            piece = word[start:end]
            token_id = vocab_dict.get(piece)

            if token_id is not None:
                tokens.append(token_id)
                start = end
                found = True
                break
        if not found:
            start += 1
    return tokens

def encode(prompt) -> list[int]:
    global vocab_dict

    words = split(prompt)

    tokens: list[int] = []

    for word in words:
        to = encode_word(word)
        for i in to:
            tokens.append(i)
    return tokens


file_content = ""
with open("data/input/functions_definition.json", "r") as file:
    file_content = file.readlines()

input = f'Functions:{file_content}\nQuestion: What is the sum of 2 and 3?\nAnswer: ' + '{"function": "'

response = ""

while True:
    # tokens = model.encode(input)
    # tokens_array = tokens[0].tolist()
    tokens_array = encode(input)

    predictions = model.get_logits_from_input_ids(tokens_array)

    next_token = np.argmax(predictions)

    word = model.decode(next_token)

    if '"' in word:
        break
    input += word
    response += word
    print(word, end = "", flush=True)


input = f'Functions:{file_content}\nQuestion: What is the sum of 2 and -3?\nAnswer: ' + '{"function": "' + response + '", "parameters": {"'

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







# the output should be like this -. 



# [
#   {
#     "prompt": "What is the sum of 2 and 3?",
#     "name": "fn_add_numbers",
#     "parameters": {
#       "a": 2,
#       "b": 3
#     }
#   }
# ]