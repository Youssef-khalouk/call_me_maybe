from pydantic import BaseModel
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

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize paths and load JSON data for functions and prompts."""
        super().__init__(*args, **kwargs)
        try:
            with open(self.functions_path, "r") as file:
                try:
                    self.functions_data = json.loads(file.read())
                    for i in self.functions_data:
                        self.functions_name.append(i["name"])
                except json.JSONDecodeError:
                    print(f"invalid functions json file '{self.functions_path}'")
        except (FileNotFoundError):
            print("there is no file name ", end="")
            print(f"'{self.functions_path}'.")
            sys.exit(1)
        
        try:
            with open(self.input_path, "r") as file:
                try:
                    self.prompts_data = json.loads(file.read())
                except json.JSONDecodeError:
                    print(f"invalid input json file '{self.input_path}'")
        except (FileNotFoundError):
            print("there is no file name ", end="")
            print(f"'{self.input_path}'.")
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
