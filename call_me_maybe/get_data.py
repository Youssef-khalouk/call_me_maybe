from pydantic import BaseModel
import json


class GetData(BaseModel):
    functions_path: str
    input_path: str
    output_path: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.functions_data: any = None

        with open(self.functions_path, "r") as file:
            try:
                self.functions_data = json.loads(file.read())
            except json.JSONDecodeError:
                print(f"invalid functions json file '{self.functions_path}'")

        with open(self.input_path, "r") as file:
            try:
                self.prompts_data = json.loads(file.read())
            except json.JSONDecodeError:
                print(f"invalid input json file '{self.input_path}'")

    def get_functions_json(self) -> any:
        return self.functions_data

    def get_prompts_json(self) -> any:
        return self.prompts_data