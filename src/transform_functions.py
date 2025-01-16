import os
import json
import argparse
import subprocess

def transform_functions(dataset):

    with open('temp-extracted.json', 'w') as f:
        json.dump(dataset, f, indent=2)

    run_snippet_transformer('temp-extracted.json', 'temp-transformed.json')

    with open('temp-transformed.json', 'r') as f:
        transformed_functions = json.load(f)

    os.remove('temp-extracted.json')
    os.remove('temp-transformed.json')

    return transformed_functions

def run_snippet_transformer(input_path, output_path):

    java17 = os.getenv('JAVA_17_BINARY')
    command = [java17, '-jar', 'snippettransformer/SnippetTransformer.jar', 'snippettransformer/config.yaml', input_path, output_path]
    subprocess.run(command)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help='input path')
    parser.add_argument('-o', type=str, required=True, help='output path')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    run_snippet_transformer(args.i, args.o)