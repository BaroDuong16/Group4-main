import subprocess
import os
from .helpers import cleanup_files, get_dir, write_to_file, run_and_combine_messsages, run_code

def compile_C_code(temp_file, compiled_executable):
    compile_result = subprocess.run(
        ['gcc', temp_file, '-o', compiled_executable],
        capture_output=True, text=True
    )
    if compile_result.returncode != 0:
        return {'error': compile_result.stderr, 'passed_tests': 0, 'numHiddenTestCases': 0}

def precheck_c(language, code, precheck_test_cases, passed_tests, numHiddenTestCases):
    try:
        temp_file = os.path.join(get_dir(language), 'temp_script.c')
        compiled_executable = os.path.join(get_dir(language), 'temp_script.exe')

        write_to_file(temp_file, code)

        compile_C_code(temp_file, compiled_executable)
        
        combined_message = run_and_combine_messsages(language, temp_file, compiled_executable, None, precheck_test_cases, numHiddenTestCases, passed_tests)
        
        cleanup_files([compiled_executable, temp_file])

    except Exception as e:
        return {'error': str(e), 'passed_tests': passed_tests, 'numHiddenTestCases': numHiddenTestCases}
    
    return combined_message

def grade_C_submission(language, student_code_file, compiled_executable, test_cases, passed_tests):
    try:
        compile_C_code(student_code_file, compiled_executable)
        
        for test in test_cases['test_cases']:
            result = run_code(language, None, test, compiled_executable, None)
            if result.stdout.strip() == test['expected_output'].strip():
                passed_tests += 1
        for hidden in test_cases['hidden_test_cases']:
            hidden_result = run_code(language, None, hidden, compiled_executable, None)
            if hidden_result.stdout.strip() == hidden['expected_output'].strip():
                passed_tests += 1

        cleanup_files([compiled_executable, student_code_file])

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return  0
    
    return passed_tests
