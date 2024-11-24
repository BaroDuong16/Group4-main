import mysql.connector
import re
import random
import string
from mysql.connector import Error, ProgrammingError, OperationalError, DataError, IntegrityError

def get_mysql_connection():
    """
    Establish a connection to the MySQL database.
    Returns the connection object if successful, otherwise raises an exception.
    """
    db_config = {
        'host': '103.174.213.139',
        'port': 3323,
        'user': 'coderbyte',
        'password': 'HBjTcb1y7!5rq',
        'database': 'coderbyte_db',
        'charset': 'utf8mb4'
    }

    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset=db_config['charset']
        )
        return conn
    except mysql.connector.Error as err:
        #print(f"Error: {err}")
        raise

def generate_random_suffix():
    """Generate a random 6-digit number."""
    length = 12  
    # Độ dài chuỗi mong muốn
    characters = string.ascii_letters + string.digits  
    # Bao gồm chữ cái và chữ số
    random_string = ''.join(random.choice(characters) for i in range(length)) 

    return random_string

def modify_table_names(query: str, suffix: str) -> str:
    """
    Modify table names by adding a suffix to the table name in both CREATE TABLE
    statements and FOREIGN KEY constraints.
    
    Args:
        query (str): The SQL query to modify.
        suffix (str): The suffix to append to the table names.
        
    Returns:
        str: The modified SQL query with the new table names.
    """
    # Regex to capture the table name after CREATE TABLE and add the suffix
    create_table_pattern = re.compile(r'(CREATE\s+TABLE\s+)(`?\w+`?)', re.IGNORECASE)
    
    # Find the main table name in CREATE TABLE and add the suffix
    modified_query = create_table_pattern.sub(lambda match: f"{match.group(1)}{match.group(2)}_{suffix}", query)
    
    # Regex to capture the table name in FOREIGN KEY references
    foreign_key_pattern = re.compile(r'(REFERENCES\s+)(`?\w+`?)', re.IGNORECASE)
    
    # Modify the table name in FOREIGN KEY constraints
    modified_query = foreign_key_pattern.sub(lambda match: f"{match.group(1)}{match.group(2)}_{suffix}", modified_query)
    
    return modified_query

def is_table_creation_query(query: str) -> bool:
    """
    Determine if the query is related to table creation or modification.
    
    Args:
        query (str): The SQL query to be checked.
    
    Returns:
        bool: True if the query is related to table creation/modification, False otherwise.
    """
    # Keywords that indicate the query involves table creation/modification
    table_keywords = ['CREATE TABLE', 'ALTER TABLE', 'DROP TABLE', 'TRUNCATE TABLE']
    
    # Check if any of the keywords are present in the query
    return any(keyword in query.upper() for keyword in table_keywords)

def extract_table_name(query: str) -> str:
    """
    Extract the table name from a SQL query, specifically for CREATE TABLE queries.
    Args:
        query (str): The SQL query string.
    Returns:
        str: The table name.
    """
    pattern = r"(CREATE\s+TABLE\s+)(\w+)"
    match = re.search(pattern, query, flags=re.IGNORECASE)
    if match:
        return match.group(2)  # Return the table name
    return None

def replace_table_name_in_test_cases(query_value: str, table_name: str, new_table_name: str) -> str:
    """
    Replace the table name in all queries and expected results within the test cases.
    
    Args:
        query_value (str): The query from test cases to be updated. 
        table_name (str): The original table name to be replaced.
        new_table_name (str): The modified table name with the random suffix.
    
    Returns:
        str: The updated query_value test cases with the new table name.
    """
    modified_test_case = re.sub(table_name, new_table_name, query_value, flags=re.IGNORECASE)
    
    return modified_test_case

def truncate_and_drop_tables(cursor, table_names):
    """
    Truncate and drop tables in reverse order of their creation to avoid foreign key constraint issues.
    
    Args:
        cursor: The database cursor.
        table_names (list): List of table names in the order they were created.
                            The last table in the list should be the one created last (dependent table).
    """
    try:
        # Reverse the order of table names to drop them in reverse order of their creation
        for table_name in reversed(table_names):
            # Truncate the table to remove all data
            cursor.execute(f"TRUNCATE TABLE {table_name};")
            # Drop the table to remove it from the database
            cursor.execute(f"DROP TABLE {table_name};")
    except mysql.connector.Error as e:
        print(f"Error truncating and dropping table {table_name}: {e}")

def execute_sql(code, test_cases):
    dict_query_student = split_queries(code)
    if isinstance(dict_query_student,str):
        return dict_query_student
    test_cases = convert_list_to_dict(test_cases)
    message = []
    passed_tests = 0
    total_tests = 0
    count = 1  # Initialize the test case counter

    # Generate a random 6-digit suffix for table names
    table_suffix = generate_random_suffix()
    table_names = []  # To store table names in the order they were created
    try:
        # Connect to the MySQL database
        conn = get_mysql_connection()
        cursor = conn.cursor()

        # Loop through each query in the student's dict_query_student
        for query_key in dict_query_student:
            student_query = dict_query_student.get(query_key)
            message_temp = ""
            # Extract the table name from the student's query for modification
            table_name = extract_table_name(student_query)
            # Check if it's a table creation exercise
            if is_table_creation_query(student_query):
                modified_table_name = f"{table_name}_{table_suffix}"

                # Modify the student's query by adding the random suffix to table names
                modified_student_query = modify_table_names(student_query, table_suffix)
                
                # Store the modified table name to truncate and drop later
                table_names.append(modified_table_name)

                # Execute the student's CREATE TABLE query
                student_result = execute_student_query(cursor, modified_student_query)

                # Run the test cases (Insert data format)
                for test_key, test_queries in test_cases.items():
                    if test_key == query_key:
                        for test_query in test_queries:
                            message_temp = f'<div style="text-align: center;"><strong>TEST CASE {count}</strong></div>'

                            # Replace all occurrences of table name in the test cases with the modified table name
                            modified_test_query = replace_table_name_in_test_cases(test_query, table_name, modified_table_name)
                            total_tests += 1  # Increment total test count for each test case
                            try:
                                cursor.execute(modified_test_query)
                                passed_tests += 1  # Increment test count if the query runs successfully
                                
                                message.append(
                                    f'<div class="alert alert-success" role="alert">'
                                    f'{message_temp}<div style="text-align: center;"><strong>&lt;&lt;&lt;&lt;&lt;&lt; PASSED &gt;&gt;&gt;&gt;&gt;&gt;</strong></div>'
                                    f'</div>'
                                )
                            except Exception as e:
                                message.append(
                                    f'<div class="alert alert-danger" role="alert">'
                                    f'<strong>Error in test case {count}:</strong> {e}<br>'
                                    f'</div>'
                                )
                            count += 1  # Increment the test case counter
            else:
                # It's a regular query exercise (e.g., SELECT, INSERT, etc.), no modification needed
                total_tests = len(test_cases)
                message_temp = f"<div style='text-align: center;'><strong>TEST CASE {count}</strong></div>"
                count += 1  # Increment the test case counter

                # Execute the student's code
                student_result = execute_student_query(cursor, student_query)  # Get the result from the student's query
                message_temp += f"<strong>Your Result:</strong>" + "&nbsp;&nbsp;&nbsp;&nbsp;" +str(student_result.get('result')) + "<br>"
                
                # Execute the expected query
                expected_query = test_cases.get(query_key)
                if expected_query:
                    cursor.execute(expected_query)
                    expected_result = cursor.fetchall()
                    message_temp += f"<strong>Expected Result:</strong>" + "&nbsp;&nbsp;&nbsp;&nbsp;" +str(expected_result) + "<br>"

                    if student_result.get('result', []) == expected_result:
                        passed_tests += 1
                        #print(f'{query_key}: Pass')
                        # Thêm nội dung vào thẻ alert success khi pass
                        message.append(
                            f'<div class="alert alert-success" role="alert">'
                            f'{message_temp}<div style="text-align: center;"><strong>&lt;&lt;&lt;&lt;&lt;&lt; PASSED &gt;&gt;&gt;&gt;&gt;&gt;</strong></div>'
                            f'</div>'
                        )
                    else:
                        error_msg = student_result.get('error',"Please check the expected Result !!!")
                        #print(f'{query_key}: Fail - Error: {error_msg}')
                        # Thêm nội dung vào thẻ alert danger khi fail
                        message.append(
                            f'<div class="alert alert-danger" role="alert">'
                            f'{message_temp} <div style="text-align: center;"><strong>{error_msg}</strong><br><strong>&lt;&lt;&lt;&lt;&lt;&lt; FAILED &gt;&gt;&gt;&gt;&gt;&gt;</strong></div>'
                            f'</div>'
                        )
        header_msg = f"""
        <div style="text-align: center;">
        <h5> <span style="color: black;"> &lt;&lt;&lt;&lt;&lt;&lt;RUNNING TEST CASES&gt;&gt;&gt;&gt;&gt;&gt;</span></h5>
        <h6> <span style="color: red;">You have passed {passed_tests} out of 
        {total_tests} total test cases. </span></h6></div><br>
        
        """
        message.insert(0, header_msg)
        
        # Truncate and drop the tables in reverse order to avoid foreign key constraint issues
        truncate_and_drop_tables(cursor, table_names)

    except mysql.connector.Error as e:
        return {'error': f"SQL Error: {e}"}
    
    finally:
        if cursor is not None:  # Check if cursor was created
            cursor.close()  # Ensure cursor is closed after execution
        if conn is not None:  # Check if connection was created
            conn.close() 
    combined_message = ''.join(message)
    return combined_message, passed_tests, total_tests

def split_queries(queries: str) -> dict:
    # Regular expression to match 'query_' followed by the number and capture the query
    pattern = r'(sql_\d+):\s*(.+?)(?=(sql_\d+:)|$)'
    
    # Find all matches using the regular expression
    matches = re.findall(pattern, queries, re.DOTALL)
    if not matches:
        return """<div class="alert alert-warning" role="alert">
    No queries found in the input string. <br> 
    Queries should start with <strong>query_1</strong>, <strong>query_2</strong>, etc.
</div>"""
    # Create a dictionary from the matches, replacing newlines with spaces
    query_dict = {match[0]: match[1].replace('\n', ' ').strip() for match in matches}
    
    return query_dict

def convert_list_to_dict(query_list):
    # Initialize an empty dictionary to hold the combined result
    query_dict = {}
    
    # Iterate through the list of dictionaries
    for query in query_list:
        # Update the dictionary with each query's key-value pair
        query_dict.update(query)
    
    return query_dict

def execute_student_query(cursor, query):
    """
    Executes a student's SQL query and handles possible errors.

    Args:
        cursor: The MySQL cursor object used to execute the query.
        query (str): The SQL query to be executed.

    Returns:
        dict: A dictionary with the result of the query or an error message.
    """
    try:
        cursor.execute(query)  # Execute the provided query
        student_result = cursor.fetchall()  # Get the result from the student's query
        return {'result': student_result}
    except ProgrammingError as e:
        #print(f"Programming Error executing student's query: {e}")
        return {'error': f"Programming Error: {e}"}
    except DataError as e:
        #print(f"Data Error executing student's query: {e}")
        return {'error': f"Data Error: {e}"}
    except IntegrityError as e:
        #print(f"Integrity Error executing student's query: {e}")
        return {'error': f"Integrity Error: {e}"}
    except OperationalError as e:
        #print(f"Operational Error executing student's query: {e}")
        return {'error': f"Operational Error: {e}"}
    except Error as e:
        #print(f"General SQL Error executing student's query: {e}")
        return {'error': f"General SQL Error: {e}"}
    except Exception as e:
        # This will catch any other type of exception that is not caught by the specific mysql.connector errors
        #print(f"Unexpected error: {e}")
        return {'error': f"Unexpected Error: {e}"}