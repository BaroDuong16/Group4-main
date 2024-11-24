import re
import subprocess
import os
from .helpers import cleanup_files, get_dir, write_to_file , run_and_combine_messsages, run_code

def compile_java_code(student_code, language):
    match = re.search(r'public\s+class\s+(\w+)', student_code)
    if not match:
        return {'error': "No public class found in the Java code.", 'passed_tests': 0}

    class_name = match.group(1)
    java_filename = os.path.join(get_dir(language), f"{class_name}.java")

    write_to_file(java_filename, student_code)

    compile_result = subprocess.run(
        ['javac', java_filename],
        capture_output=True, text=True
    )
    if compile_result.returncode != 0:
        return {'error': compile_result.stderr, 'passed_tests': 0}
    return class_name, java_filename

def precheck_java(language, code, precheck_test_cases, passed_tests, numHiddenTestCases):
    try:
        class_name, java_filename = compile_java_code(code, language)

        combined_message = run_and_combine_messsages(language, java_filename, None, class_name, precheck_test_cases, numHiddenTestCases, passed_tests)
        cleanup_files([java_filename, os.path.join(get_dir(language), f"{class_name}.class")])

    except Exception as e:
        return {'error': str(e), 'passed_tests': passed_tests, 'numHiddenTestCases': numHiddenTestCases}
    
    return combined_message

def grade_Java_submission(language, student_code, class_name, test_cases, passed_tests):
    try:
        class_name, java_filename = compile_java_code(student_code, language)
        
        for test in test_cases['test_cases']:
            result = run_code(language, None, test, None, class_name)
            if result.stdout.strip() == test['expected_output'].strip():
                passed_tests += 1
        for hidden in test_cases['hidden_test_cases']:
            hidden_result = run_code(language, None, hidden, None, class_name)
            if hidden_result.stdout.strip() == hidden['expected_output'].strip():
                passed_tests += 1

        cleanup_files([java_filename, os.path.join(get_dir(language), f"{class_name}.class")])

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return  0
    
    return passed_tests