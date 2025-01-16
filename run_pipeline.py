import json
import argparse
from src import extract_functions, transform_functions, combine, get_summarized_stack_traces

def run_pipeline_with_transform(dataset):

    print("Extracting functions...")
    extracted_functions = extract_functions(dataset)
    print("Transforming functions...")
    transformed_functions = transform_functions(extracted_functions)
    print("Running defects4j tests...")
    stack_traces = get_summarized_stack_traces(dataset, transformed_functions, amount_of_threads=args.thr)
    print("Combining results...")
    return combine(dataset, stack_traces, transformed_functions)


def run_pipeline_without_transform(dataset):
    print("Running defects4j tests...")
    stack_traces = get_summarized_stack_traces(dataset, amount_of_threads=args.thr)
    print("Combining results...")
    return combine(dataset, stack_traces)



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help='input path')
    parser.add_argument('-t', type=bool, required=False, default=False, help='transform functions')
    parser.add_argument('-o', type=str, required=True, help='output path')
    parser.add_argument('-thr', type=int, required=False, default=1, help='number of threads')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    with open(args.i, 'r') as f:
        dataset = json.load(f)
    if args.t:
        result = run_pipeline_with_transform(dataset)
    else:
        result = run_pipeline_without_transform(dataset)

    with open(args.o, 'w') as f:
        json.dump(result, f, indent=2)