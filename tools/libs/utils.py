
import pandas as pd
import json
import re

from io import BytesIO

from docx import Document

# Function to generate exams
def generator(excel_file, number_of_questions):
    temp = []
    count = 1
    for name, question in number_of_questions.items():
        # Read the specific sheet into a DataFrame
        data = pd.read_excel(excel_file, sheet_name=name)

        #if 'Exam Number'
        
        # Extract the specified number of random rows from the sheet
        extract = data.sample(question)

        #index = extract.index

        #count += 1

        # Append the extracted rows to the list
        temp.append(extract)
    
    # Combine all the DataFrames in the list into a single DataFrame
    df_combined = pd.concat(temp, ignore_index=True)

    # Write the combined DataFrame to a new Excel file in memory
    output = BytesIO()
    df_combined.to_excel(output, index=False)
    output.seek(0)
    
    return output, df_combined

def arrange_answers(answers, correct_label):
    correct_index = ord(correct_label.upper()) - ord('A')
    answers.insert(0, answers.pop(correct_index))
    return answers

def clean_text(text):
    text = re.sub(r'<', '&lt;', text)
    text = re.sub(r'>', '&gt;', text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n', '<br>', text)
    return text.strip()

def excel_to_json(data):
    # Prepare the JSON structure
    output_structure = {"mc_questions": []}
    print(data)

    for index, row in data.iterrows():
        try:

            print(index)
            # Extract question and answers
            answers = [row[f'options[{label.lower()}]'] for label in 'ABCDEFG' if pd.notnull(row[f'options[{label.lower()}]'])]
            correct_label = row['correct'].strip().upper()
            # Arrange answers based on the correct label
            arranged_answers = arrange_answers(answers, correct_label) if correct_label in 'ABCDEFG' else answers

            cleaned_question = clean_text(str(row['question']))
            cleaned_answers = [clean_text(str(answer)) for answer in arranged_answers]


            question_data = {
                "question": cleaned_question,
                "answers": cleaned_answers
            }
            # Add the question data to the list
            output_structure["mc_questions"].append(question_data)
        except KeyError as e:
            print(f"KeyError: {e} at row {index}")
        except Exception as e:
            print(f"Unexpected error: {e} at row {index}")

    # Convert the output structure to a JSON string
    json_data = json.dumps(output_structure, indent=4, ensure_ascii=False)
    
    return json_data

def word_to_json(content):
    # Khởi tạo cấu trúc JSON
    output_structure = {"mc_questions": []}
    
    question_text = ""
    answers = []
    correct_answer = ""
    
    for line in content.splitlines():
        text = line.strip()
        
        # Kiểm tra nếu là câu hỏi
        if text.startswith("Q:"):
            # Nếu đã có câu hỏi trước đó, lưu nó vào cấu trúc JSON
            if question_text:
                question_data = {
                    "question": question_text,
                    "answers": answers,
                    "correct": correct_answer
                }
                output_structure["mc_questions"].append(question_data)
                
            # Reset cho câu hỏi mới
            question_text = text[2:].strip()  # Lấy phần sau "Q:"
            answers = []
            correct_answer = ""
        
        # Kiểm tra nếu là đáp án
        elif re.match(r'^[A-Z]\.\s', text):
            answers.append(text)  # Thêm đáp án vào danh sách
            
        # Kiểm tra nếu là đáp án đúng
        elif text.startswith("Correct:"):
            correct_answer = text.split(":")[1].strip()  # Lấy phần sau "Correct:"

    # Lưu câu hỏi cuối cùng nếu có
    if question_text:
        question_data = {
            "question": question_text,
            "answers": answers,
            "correct": correct_answer
        }
        output_structure["mc_questions"].append(question_data)
    
    # Chuyển đổi cấu trúc JSON sang chuỗi
    json_data = json.dumps(output_structure, indent=4, ensure_ascii=False)
    
    return json_data


