from pydantic import BaseModel, model_validator
import json
from typing import Any
import sys


class GetData(BaseModel):
    """Load function definitions and prompts from JSON files."""
    functions_path: str
    input_path: str
    output_path: str

    functions_data: Any = None
    prompts_data: Any = None
    functions_name: list[str] = []

    @model_validator(mode="after")
    def validate_json_content(self) -> None:
        """Validate the content of the JSON files after initialization."""
        if self.functions_path.endswith(".json") is False:
            print("the functions definition file "
                  f"'{self.functions_path}' must be a json file",
                  file=sys.stderr)
            sys.exit(1)
        if self.input_path.endswith(".json") is False:
            print("the input file "
                  f"'{self.input_path}' must be a json file",
                  file=sys.stderr)
            sys.exit(1)
        if self.output_path.endswith(".json") is False:
            print("the output file "
                  f"'{self.output_path}' must be a json file",
                  file=sys.stderr)
            sys.exit(1)
        self.load_data()
        for function in self.functions_data:
            name = function.get("name", None)
            if name is None:
                print("the json dosn't have the 'name' key", file=sys.stderr)
                sys.exit(1)
            else:
                if not isinstance(name, str):
                    print("the 'name' key must be a string", file=sys.stderr)
                    sys.exit(1)
                elif name == "":
                    print("the 'name' key must not be empty", file=sys.stderr)
                    sys.exit(1)
            description = function.get("description", None)
            if description is None:
                print("the json dosn't have the 'description' key",
                      file=sys.stderr)
                sys.exit(1)
            else:
                if not isinstance(description, str):
                    print("the 'description' key must be a string",
                          file=sys.stderr)
                    sys.exit(1)
            parameters = function.get("parameters", None)
            if parameters is None:
                print("the json dosn't have the 'parameters' key",
                      file=sys.stderr)
                sys.exit(1)
            else:
                if not isinstance(parameters, dict):
                    print("the 'parameters' key must be a dictionary",
                          file=sys.stderr)
                    sys.exit(1)
                else:
                    if parameters == {}:
                        print("the 'parameters' dictionary must not be empty",
                              file=sys.stderr)
                        sys.exit(1)
                    for k, v in parameters.items():
                        if not isinstance(k, str):
                            print(f"the key '{k}' of the 'parameters' "
                                  "dictionary must be strings",
                                  file=sys.stderr)
                            sys.exit(1)
                        if not isinstance(v, dict):
                            print(f"the value '{v}' of the 'parameters' "
                                  "dictionary must be dictionaries",
                                  file=sys.stderr)
                            sys.exit(1)
                        else:
                            type_ = v.get("type", None)
                            if type_ is None:
                                print(f"the parameter '{k}' dosn't have "
                                      "the 'type' key", file=sys.stderr)
                                sys.exit(1)
                            else:
                                if not isinstance(type_, str):
                                    print("the 'type' key of the parameter "
                                          f"'{k}' must be a string",
                                          file=sys.stderr)
                                    sys.exit(1)
                                if type_ == "":
                                    print(f"the 'type' key of the parameter "
                                          f"'{k}' must not be empty",
                                          file=sys.stderr)
                                    sys.exit(1)
            returns_ = function.get("returns", None)
            if returns_ is None:
                print("the json dosn't have the 'returns' key",
                      file=sys.stderr)
                sys.exit(1)
            else:
                if not isinstance(returns_, dict):
                    print("the 'returns' key must be a dictionary",
                          file=sys.stderr)
                    sys.exit(1)
                else:
                    type_ = returns_.get("type", None)
                    if type_ is None:
                        print("the 'returns' dictionary dosn't "
                              "have the 'type' key", file=sys.stderr)
                        sys.exit(1)
                    else:
                        if not isinstance(type_, str):
                            print("the 'type' key of the 'returns' dictionary "
                                  "must be a string", file=sys.stderr)
                            sys.exit(1)
                        if type_ == "":
                            print("the 'type' key of the 'returns' dictionary "
                                  "must not be empty", file=sys.stderr)
                            sys.exit(1)

        for prompt in self.prompts_data:
            prompt_name = prompt.get("prompt", None)
            if prompt_name is None:
                print("the prompts json file must have the 'prompt' key",
                      file=sys.stderr)
                sys.exit(1)
            if not isinstance(prompt_name, str):
                print("the prompts value must be strings", file=sys.stderr)
                sys.exit(1)

    def load_data(self) -> None:
        """
        Load function definitions and prompts from the specified JSON files.
        """
        try:
            with open(self.functions_path, "r") as file:
                try:
                    self.functions_data = json.load(file)
                    for i in self.functions_data:
                        self.functions_name.append(i["name"])
                except json.JSONDecodeError:
                    print("invalid functions json file", end="",
                          file=sys.stderr)
                    print(f"'{self.functions_path}'", file=sys.stderr)
        except (FileNotFoundError):
            print("there is no file name ", end="", file=sys.stderr)
            print(f"'{self.functions_path}'.", file=sys.stderr)
            sys.exit(1)

        try:
            with open(self.input_path, "r") as file:
                try:
                    self.prompts_data = json.load(file)
                except json.JSONDecodeError:
                    print(f"invalid input json file '{self.input_path}'",
                          file=sys.stderr)
        except (FileNotFoundError):
            print("there is no file name ", end="", file=sys.stderr)
            print(f"'{self.input_path}'.", file=sys.stderr)
            sys.exit(1)

    def get_functions_json(self) -> Any:
        """Return the loaded function definitions JSON."""
        return self.functions_data

    def get_prompts_json(self) -> Any:
        """Return the loaded prompts JSON."""
        return self.prompts_data

    def get_functions_name(self) -> list[str]:
        """Return the list of available function names."""
        return self.functions_name

    def get_output_path(self) -> str:
        """Return the configured output file path."""
        return self.output_path
