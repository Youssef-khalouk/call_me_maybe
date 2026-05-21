import argparse
from .get_data import GetData
from .my_model import My_Model
import numpy as np

def is_in(functions_name: list[str], token: str) -> bool:
    for function in functions_name:
        if token in function:
            return True
    return False

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition")
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()

    data = GetData(
        functions_path = args.functions_definition,
        input_path = args.input,
        output_path = args.output)
    functions_name = data.get_functions_name()

    model = My_Model()

    # tokens = model.encode("fn_substitute_string_with_regex")
    # for t in tokens:
    #     print(model.decode(t))

    for p in data.get_prompts_json():
        prompt = f'Functions: {data.get_functions_json()} Question:{p["prompt"]}'+' Answer: {"function": "fn'
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
                        print(f"\nthere is no function name -> '{answer}'")
                        c_prompt = prompt
                        answer = ""
                        break;
                    
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
    print("")

