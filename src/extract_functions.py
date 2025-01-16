import json
import argparse

def extract_functions(dataset):
    functions = {}

    for bug_id in dataset:
        functions[bug_id] = dataset[bug_id]['buggy_function']

    return functions


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help='input path')
    parser.add_argument('-o', type=str, required=True, help='output path')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    with open(args.i, 'r') as f:
        dataset = json.load(f)

    functions = extract_functions(dataset)

    with open(args.o, 'w') as f:
        json.dump(functions, f, indent=2)