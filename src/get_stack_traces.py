import os
import shutil
import json
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
try:
    from src.summarize_stack_trace import summarize_stack_traces
except ImportError:
    from summarize_stack_trace import summarize_stack_traces


def get_summarized_stack_traces(dataset, transformed_functions=None, amount_of_threads=1):
    stack_traces = {}

    with ThreadPoolExecutor(max_workers=amount_of_threads) as executor:
        jobs = []
        for bug_id in dataset:
            bug = dataset[bug_id]
            job = start_job(bug, executor, transformed_functions)
            jobs.append((job, bug_id))

        for job, bug_id in tqdm(jobs):
            stack_traces[bug_id] = get_result(job)

    return stack_traces

def start_job(bug, executor, transformed_functions = None):
    if transformed_functions:
        return executor.submit(get_failing_tests_for, bug, transformed_functions[bug['id']])
    return executor.submit(get_failing_tests_for, bug)

def get_result(job):
    try:
        return job.result()
    except Exception as e:
        print(e)
        return {"Problem": "No stack traces could be obtained."}

def get_failing_tests_for(bug, transformed_function = None):
    working_directory = f'tmp/{bug["id"]}'

    safe_remove(working_directory)

    checkout_defects4j_project(bug['project'], bug['number'], working_directory)
    if transformed_function:
        replace_function(bug['replacement_info'], transformed_function, working_directory)
    compile_defects4j_project(working_directory)
    test_defects4j_project(working_directory)

    stack_traces = summarize_stack_traces(working_directory)

    safe_remove(working_directory)

    return stack_traces

def safe_remove(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)

def checkout_defects4j_project(project, bug_number, working_directory):
    command = ["defects4j", "checkout", "-p", project, "-v", f"{bug_number}b", "-w", working_directory]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr)

def replace_function(replacement_info, transformed_function, clone_directory):
    first_line = replacement_info['first_line']
    last_line = replacement_info['last_line']

    file_path = os.path.join(clone_directory, replacement_info['file'])
    with open(file_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = lines[:first_line - 1] + transformed_function.splitlines(keepends=True) + lines[last_line:]

    with open(file_path, 'w', encoding="utf-8") as f:
        f.writelines(new_lines)

def compile_defects4j_project(working_directory):
    command = ["defects4j", "compile", '-w', working_directory]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr)

def test_defects4j_project(working_directory):
    command = ["defects4j", "test", '-w', working_directory]
    result = subprocess.run(command, capture_output=True, text=True, timeout=10 * 60)
    if result.returncode != 0:
        raise Exception(result.stderr)

def get_failing_test_output(working_directory):
    with open(os.path.join(working_directory, 'failing_tests'), 'r') as f:
        return f.read()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, required=True, help='dataset path')
    parser.add_argument('-t', type=str, required=False, default=None, help='transformed functions path')
    parser.add_argument('-o', type=str, required=True, help='output path')
    parser.add_argument('-thr', type=int, required=False, default=1, help='number of threads')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    with open(args.d, 'r') as f:
        dataset = json.load(f)

    if args.t is not None:
        with open(args.t, 'r') as f:
            transformed_functions = json.load(f)
        stack_traces = get_summarized_stack_traces(dataset, transformed_functions, amount_of_threads=args.thr)
    else:
        stack_traces = get_summarized_stack_traces(dataset, amount_of_threads=args.thr)


    with open(args.o, 'w') as f:
        json.dump(stack_traces, f, indent=2)