import os
import re
import chardet

def summarize_stack_traces(working_directory):
    raw_stack_traces = get_raw_stack_traces(working_directory)
    build_properties = parse_build_properties(working_directory)
    summarized_error_messages = {}

    for test_name in raw_stack_traces:
        raw_stack_trace = raw_stack_traces[test_name]
        filtered_stack_trace = filter_stack_trace(raw_stack_trace, build_properties)

        stack_trace_with_appended_code = append_code_lines(filtered_stack_trace, build_properties, working_directory)
        summarized_error_messages[test_name] = stack_trace_with_appended_code


    return summarized_error_messages

def get_raw_stack_traces(working_directory):
    with open(os.path.join(working_directory, 'failing_tests'), 'r') as f:
        failing_tests_output = f.read()

    error_messages = split_error_messages(failing_tests_output)

    stack_traces = {}

    for error_message in error_messages:
        test_name, stack_trace = split_stack_trace_and_test_name(error_message)
        stack_traces[test_name] = stack_trace

    return stack_traces

def split_error_messages(error_messages_string: str):
    return error_messages_string.strip().split('--- ')[1:]

def split_stack_trace_and_test_name(error_message: str):
    error_message = error_message.strip()

    lines = error_message.splitlines()
    test_name = lines[0]
    stack_trace = '\n'.join(lines[1:])

    return test_name, stack_trace


def parse_build_properties(working_directory):
    build_properties = {}
    with open(os.path.join(working_directory, 'defects4j.build.properties'), 'r') as f:
        lines = f.readlines()

    for line in lines[1:]:
        key = line.split('=')[0]
        value = line.split('=')[1].strip()
        if len(value.split(',')) > 1:
            value = value.split(',')

        build_properties[key] = value
    return build_properties

def filter_stack_trace(stack_trace: str, build_properties: dict):
    raw_lines = stack_trace.splitlines()
    filtered_lines = [raw_lines[0]]
    for line in raw_lines[1:]:
        if is_relevant_line(line, build_properties):
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def is_relevant_line(line: str, build_properties: dict):
    relevant_classes = build_properties['d4j.classes.relevant']
    trigger_tests = build_properties['d4j.tests.trigger']

    # Sometimes they are a list of strings and sometimes they are only 1 string.
    if isinstance(relevant_classes, str):
        relevant_classes = [relevant_classes]
    if isinstance(trigger_tests, str):
        trigger_tests = [trigger_tests]

    for class_name in relevant_classes:
        if class_name in line:
            return True

    for trigger_test in trigger_tests:
        if trigger_test.split('::')[0] in line:
            return True
    return False

def append_code_lines(filtered_stack_trace: str, build_properties, working_directory):
    filtered_stack_trace_lines = filtered_stack_trace.splitlines()
    result = [filtered_stack_trace_lines[0]]
    for line in filtered_stack_trace_lines[1:]:
        if refers_to_code_line(line):
            file_path = get_file_path(line, working_directory, build_properties)
            line_number = get_line_number(line)
            code_line = get_code_line(file_path, line_number)
            result.append(line + "  " + code_line)
    return '\n'.join(result)

def refers_to_code_line(line):
    return not line.startswith("Caused by:") and not line.endswith("(<generated>)")

def get_file_path(line, working_directory, build_properties):
    # Remove the "  at " part of the line
    at_removed = re.sub("\tat |-> at ", "", line)
    # Extract the file
    class_file = re.findall(r"\((.*):\d+\)", at_removed)[0]
    # Remove the "(Class.java:number)" part of the stack trace
    package = re.sub(r"\(.*\)", "", at_removed)


    # The part after the last . is the method call and should not appear in the path
    package_path_directories = package.split('.')[:-2]

    # Check both in the source and test directories
    src_path = os.path.join(working_directory, build_properties['d4j.dir.src.classes'], *package_path_directories, class_file)
    tests_path = os.path.join(working_directory, build_properties['d4j.dir.src.tests'], *package_path_directories, class_file)

    if os.path.exists(src_path):
        return src_path
    return tests_path

def get_line_number(line):
    line_number = re.search(":(\d+)", line).group(1)
    return int(line_number)

def get_code_line(file_path, line_number):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except UnicodeDecodeError as e:
        with open(file_path, 'r', encoding='ISO-8859-1') as f:
            lines = f.readlines()
    # First line of the file has index 0.
    return lines[line_number - 1].strip()

