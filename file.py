import re
import sys
import argparse
from pydantic import ValidationError as PydanticValidationError
from src.helpers import Helpers, Model
from src.exceptions import ValidationError, GenerationError
from src.validators import FunctionValidator, PromptValidator

class CallMeMaybe:
    def __init__(self):
        self._model = Model()

    def parse(self) -> argparse.Namespace:
        arguments = argparse.ArgumentParser(
            description="LLM function calling system."
        )
        arguments.add_argument(
            "--functions_definition",
            default="data/input/functions_definition.json",
            help="Path to function definition file.",
        )
        arguments.add_argument(
            "--input",
            default="data/input/function_calling_tests.json",
            help="Path to input prompts file.",
        )
        arguments.add_argument(
            "--output",
            default="data/output/function_calling_results.json",
            help="Path to output file.",
        )
        return arguments.parse_args()

    def validate(self, functions: list[dict], prompts: list[dict]) -> None:
        try:
            for function in functions:
                FunctionValidator(**function)
        except Exception:
            raise ValidationError("Fail to validate functions")
        try:
            for prompt in prompts:
                PromptValidator(**prompt)
        except Exception as exception:
            print(exception)
            raise ValidationError("Fail to validate prompts")

    def generate_function(self, functions: list[dict], question: str) -> str:
        output = ""
        prompt = f"Functions: {functions}\n"
        prompt += f"Question: {question}\n"
        prompt += 'Answer: {"function_name": "'
        names: list[str] = list(map(lambda i: i['name'], functions))
        while True:
            raw_logits = self._model.logits(self._model.encode(prompt))
            logits = Helpers.sortDictByKey(raw_logits, 'score')
            while logits[0]['score'] > 0:
                possible_token = logits[0]['content']
                if '"' in possible_token:
                    break
                fn_name = f"{output}{possible_token}"
                if len(list(filter(lambda n: n.startswith(fn_name), names))):
                    names = list(filter(lambda n: n.startswith(fn_name), names))
                    break
                else:
                    logits[0]['score'] = logits[0]['score'] * -1
                    logits = Helpers.sortDictByKey(logits, 'score')
            chosen_token = logits[0]['content']
            if '"' in chosen_token:
                break
            prompt += chosen_token
            output += chosen_token
        return output

    def generate_argument(self, fn: dict, qst: str, prms: dict, key: str) -> dict:
        output = ""
        prompt = f"Function: {fn}\n"
        prompt += f"Question: {qst}\n"
        prompt += 'Answer: {"function_name": "' + fn['name'] + '", "parameters": {'
        index = 0
        for k, v in prms.items():
            if index > 0:
                prompt += ', '
            prompt += f'"{k}": "{v}"'
        if index > 0:
            prompt += ', '
        prompt += f'"{key}": '
        if fn['parameters'][key]['type'] in ['string']:
            prompt += '"'
        generating = True
        while generating:
            raw_logits = self._model.logits(self._model.encode(prompt + output))
            logits = Helpers.sortDictByKey(raw_logits, 'score')
            while generating and logits[0]['score'] > 0:
                token = logits[0]['content']
                if fn['parameters'][key]['type'] in ['string']:
                    token = token.split('"')
                    if len(token) > 1:
                        generating = False
                    output += token[0]
                    break
                if fn['parameters'][key]['type'] in ['number', 'integer']:
                    token = re.split(r",|}", token)
                    if len(token) > 1:
                        generating = False
                    if not Helpers.isValidNumber(token[0]):
                        logits[0]['score'] = logits[0]['score'] * -1
                        logits = Helpers.sortDictByKey(logits, 'score')
                        continue
                    output += token[0]
                    break
        return output.replace('\\\\', '\\')


if __name__ == "__main__":
    try:
        index: int = 0
        app = CallMeMaybe()
        arguments = app.parse()
        Helpers.validateJSONFile(arguments.functions_definition)
        Helpers.validateJSONFile(arguments.input)
        Helpers.safeFileTouch(arguments.output)
        functions = Helpers.loadJSON(arguments.functions_definition)
        prompts = Helpers.loadJSON(arguments.input)
        app.validate(functions, prompts)
        result = []
        for prompt in map(lambda p: p['prompt'], prompts):
            index += 1
            search = []
            print(f"{index}/{len(prompts)}  ", end="", flush=True)
            iters = 0
            while not search and iters <= 10:
                fn_name = app.generate_function(functions, prompt)
                search = list(filter(lambda fn: fn['name'] == fn_name, functions))
            if iters == 10:
                raise GenerationError("Fail to find function for prompt:", prompt)
            fn = search[0]
            print(fn_name, end="", flush=True)
            parameters: dict = {}
            for key, value in fn['parameters'].items():
                argument = app.generate_argument(fn, prompt, parameters, key)
                parameters.update({key: argument})
                if Helpers.isValidNumber(argument):
                    if fn['parameters'][key]['type'] == 'number':
                        parameters.update({key: float(argument)})
                    if fn['parameters'][key]['type'] == 'integer':
                        parameters.update({key: int(argument)})
                elif Helpers.isValidBoolean(argument):
                    if fn['parameters'][key]['type'] == 'boolean':
                        parameters.update({key: bool(argument)})
                print(f"    {argument}", end="", flush=True)
            print()
            result.append({
                "prompt": prompt,
                "name": fn_name,
                "parameters": parameters,
            })
            Helpers.saveJSONFile(arguments.output, result)
    except ValidationError as exception:
        print(f"\033[31mValidationError:\033[0m {exception}", file=sys.stderr)
    except GenerationError as exception:
        print(f"\033[31mGenerationError:\033[0m {exception}", file=sys.stderr)