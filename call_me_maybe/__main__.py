import argparse
from .get_data import GetData
from .my_model import My_Model
import numpy as np
import os
import json


def is_in(functions_name: list[str], token: str) -> bool:
    for function in functions_name:
        if token in function:
            return True
    return False


def generate_parameters(function_json: any) -> list[str]:
    paramters = function_json["parameters"]
    array = []
    for p in paramters:
        array.append(p)
    return array


json_content = []


def save_in_file(file_path):
    with open(file_path, "w") as file:
        file.write(json.dumps(json_content, indent=4))


def get_paramters(model: any, function_json: any, questoin: str) -> dict:
    paramters = generate_parameters(function_json)
    prompt = (
        f'/nothink\nFunctions:{function_json}\n'
        f'Question: {questoin}\nParameters: '
        '{"function": "' + function_json["name"] + '", "parameters": '
    )
    para_answer = {}
    print("   ", end="", flush=True)
    prompt += '{'
    for p in paramters:
        prompt += '"' + p + '":'
        if (function_json["parameters"][p]["type"]) == "string":
            prompt += '"'

        answer = ""
        print(f' "{p}": ', end="", flush=True)
        while True:
            next_token = model.get_next_token(prompt)
            if '"' in next_token:
                before_quote = next_token.split('"')[0]
                answer += before_quote
                if (function_json["parameters"][p]["type"]) == "string":
                    prompt += '", '
                else:
                    prompt += ', '
                break
            if '}' in next_token:
                count1 = answer.count("{")
                count2 = answer.count("}")
                if count1 - count2 <= 0:
                    break
            answer += next_token
            prompt += next_token
        if function_json["parameters"][p]["type"] == "number":
            num = answer.strip().replace("\\\\", "\\")
            if num.endswith(","):
                num = num[0:-1]
            para_answer[p] = float(num)
        elif function_json["parameters"][p]["type"] == "integer":
            num = answer.strip().replace("\\\\", "\\")
            if num.endswith(","):
                num = num[0:-1]
            para_answer[p] = int(num)
        else:
            para_answer[p] = answer.strip().replace("\\\\", "\\")
        print(para_answer[p], end="", flush=True)
    return para_answer


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition")
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()

    data = GetData(
        functions_path=args.functions_definition,
        input_path=args.input,
        output_path=args.output)
    functions_name = data.get_functions_name()
    os.makedirs(os.path.dirname(data.get_output_path()), exist_ok=True)

    model = My_Model()

    for p in data.get_prompts_json():
        prompt = f'Functions: {data.get_functions_json()} '
        prompt += f'Question:{p["prompt"]}'
        prompt += ' Answer: {"function": "fn'
        print("\nfn", end="", flush=True)
        c_prompt = prompt
        answer = "fn"
        while True:
            tokens = model.encode(c_prompt)
            logits = model.get_logits(tokens)
            top_logits = np.argsort(logits)[-50:]
            next_token = ""
            found = False
            for i in range(1, 50):
                token = model.decode(top_logits[-i])
                if '"' in token:
                    if answer in functions_name:
                        found = True
                        break
                    else:
                        c_prompt = prompt
                        answer = ""
                        break
                if (is_in(functions_name, f'{answer}{token}')):
                    print(token, end="", flush=True)
                    next_token = token
                    found = True
                    break
            if not found:
                print("<- not found -> ", token)
                continue
            if '"' in token:
                break
            answer += next_token
            c_prompt += next_token

        for function in data.get_functions_json():
            if function["name"] == answer:
                parameters = get_paramters(model, function, p["prompt"])
                function_json = {}
                function_json["prompt"] = p["prompt"]
                function_json["name"] = function["name"]
                function_json["parameters"] = parameters
                json_content.append(function_json)
                save_in_file(data.get_output_path())
                break

    print("")
