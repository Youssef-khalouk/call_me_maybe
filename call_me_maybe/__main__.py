import argparse
from .get_data import GetData
from .my_model import My_Model


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

    print(data.get_functions_json().dump())

