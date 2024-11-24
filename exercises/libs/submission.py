import json

from .helpers import prepare_file_paths, write_to_file, calculate_score
from .c_helpers import grade_C_submission, precheck_c
from .java_helpers import grade_Java_submission, precheck_java
from .python_helpers import grade_Python_submission, precheck_python
from .sql_helpers import execute_sql


def grade_submission(submission):
    # Get student's code and language
    student_code = submission.code
    language = submission.exercise.language # 'python', 'java', or 'c'
    # Load test cases for Python or parse JSON for Java/C
    test_cases = json.loads(submission.exercise.test_cases)
    if language != 'mysql':
        precheck_test_cases = test_cases.get('test_cases')
        numHiddenTestCases = len(test_cases.get('hidden_test_cases'))
        total_tests = len(precheck_test_cases) + numHiddenTestCases

        # Define file paths based on the language
        student_code_file, compiled_executable, class_name = prepare_file_paths(language, student_code)
        # Write student code to a file
        write_to_file(student_code_file, student_code)
        
    passed_tests = 0

    match language:
        case 'python':
            passed_tests = grade_Python_submission(language, student_code_file, test_cases, passed_tests)
        case 'c':
            passed_tests = grade_C_submission(language, student_code_file, compiled_executable, test_cases, passed_tests)
            print(passed_tests)
        case 'java':
            passed_tests = grade_Java_submission(language, student_code, class_name, test_cases, passed_tests)
        case 'mysql':
            _ , passed_tests, total_tests = execute_sql(student_code, test_cases)
    score = calculate_score(passed_tests, total_tests)
    return score

def precheck(code, language, test_cases):
    if language != 'mysql':
        precheck_test_cases = test_cases.get('test_cases')
        numHiddenTestCases = len(test_cases.get('hidden_test_cases'))
    passed_tests = 0

    match language:
        case 'python':
            combined_message = precheck_python(language, code, precheck_test_cases, passed_tests, numHiddenTestCases)
        case 'c':
            combined_message = precheck_c(language, code, precheck_test_cases, passed_tests, numHiddenTestCases)
        case 'java':
            combined_message = precheck_java(language, code, precheck_test_cases, passed_tests, numHiddenTestCases)
        case 'mysql':
            combined_message, _, _ = execute_sql(code, test_cases)

    return {'combined_message': combined_message}