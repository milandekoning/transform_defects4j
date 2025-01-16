import json
import argparse

def clean_dataset(dataset):
    clean_bugs = {}

    for bug_id in dataset:
        clean_bugs[bug_id] = clean(dataset[bug_id], bug_id)

    return clean_bugs

def clean(raw_bug, bug_id):
    replacement_info = {
        'file': raw_bug['loc'],
        'first_line': raw_bug['start'],
        'last_line': raw_bug['end']
    }

    failing_tests = {}

    for failing_test in raw_bug['trigger_test']:
        failing_tests[failing_test] = {
            'source': raw_bug['trigger_test'][failing_test]['src'],
        }

    return {
        'id': bug_id,
        'project': bug_id.split('-')[0],
        'number': bug_id.split('-')[1],
        'buggy_function': raw_bug['buggy'],
        'fixed_function': raw_bug['fix'],
        'replacement_info': replacement_info,
        'javadoc': raw_bug['buggy_code_comment'],
        'failing_tests': failing_tests
    }

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help='input path')
    parser.add_argument('-o', type=str, required=True, help='output path')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    with open(args.i, 'r') as f:
        raw_dataset = json.load(f)

    cleaned_dataset = clean_dataset(raw_dataset)

    with open(args.o, 'w') as f:
        json.dump(cleaned_dataset, f, indent=2)

