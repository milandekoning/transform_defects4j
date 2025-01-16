import json
import argparse

def combine(dataset, stack_traces, transformed_functions=None):

    output = {}
    for bug_id in dataset:
        if transformed_functions:
            output[bug_id] = combine_bug(dataset[bug_id], stack_traces[bug_id], transformed_functions[bug_id])
        else:
            output[bug_id] = combine_bug(dataset[bug_id], stack_traces[bug_id])

    return output

def combine_bug(bug, stack_traces, transformed_function = None):
    if transformed_function:
        bug['buggy_function'] = transformed_function

    for failing_test in bug['failing_tests']:
        bug['failing_tests'][failing_test]['stack_trace_summary'] = stack_traces[failing_test]
    return bug

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, required=True, help='dataset path')
    parser.add_argument('-t', type=str, required=False, default=None, help='transformed functions path')
    parser.add_argument('-s', type=str, required=True, help='stack_traces path')
    parser.add_argument('-o', type=str, required=True, help='output path')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    with open(args.d, 'r') as f:
        dataset = json.load(f)

    with open(args.s, 'r') as f:
        stack_traces = json.load(f)

    if args.t is not None:
        with open(args.t, 'r') as f:
            transformed_functions = json.load(f)
        combined_dataset = combine(dataset, stack_traces, transformed_functions)
    else:
        combined_dataset = combine(dataset, stack_traces)

    with open(args.o, 'w') as f:
        json.dump(combined_dataset, f, indent=2)

