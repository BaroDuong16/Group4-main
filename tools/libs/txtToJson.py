import json
import re
import os

def clean_text(text):
    text = text.replace("\t", "")
    text = re.sub(r'(<br>)+', '<br>', text)
    return text

def escape_special_characters(text):
    text = re.sub(r'<', '&lt;', text)
    text = re.sub(r'>', '&gt;', text)
    #replace("&", "&amp;").
    #escaped_text = text.replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")
    return  text

def extract_code_name(text):
    pattern = r'Code:?\s*(\S+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def txt_to_json(file_like, file_name):
    lines = file_like.readlines()
    output_structure = {"mc_questions": []}
    question_text = ""
    answers = []
    started = False

    for line in lines:
        line = line.strip()
        if not started:
            if line.startswith('1'):
                started = True
            continue

        question_match = re.match(r'^\s*(\d+)\.?\s+(.*)', line)
        if question_match:
            if question_text:  # Nếu có câu hỏi trước đó, lưu nó vào output
                output_structure["mc_questions"].append({
                    "question": question_text,
                    "answers": answers
                })
            question_text = question_match.group(2)
            answers = []  # Reset danh sách câu trả lời cho câu hỏi mới

        answer_match = re.match(r'^[A-M]\.\s+(.*)', line)
        if answer_match:
            answers.append(answer_match.group(1).strip())

    # Lưu câu hỏi cuối cùng nếu có
    if question_text:
        output_structure["mc_questions"].append({
            "question": question_text,
            "answers": answers
        })

    return json.dumps(output_structure, indent=4, ensure_ascii=False)

# # def txt_to_json(file_like, file_name):
#     # Read the lines from the file-like object
#     lines = file_like.readlines()

#     # Initialize the data structure to store the questions and answers
#     output_structure = {"mc_questions": []}
#     question_text = ""
#     answers = []
#     started = False
#     question_number = 0

#     # Process each line in the text file
#     for line in lines:
#         if not started:
#             if line.strip().startswith('1'):
#                 started = True
#             else:
#                 continue

#         question_match = re.match(r'^\s*(\d+)\.?\s+(.*)', line, re.IGNORECASE)
#         if question_match:
#             current_number = int(question_match.group(1))
#             if current_number == question_number + 1:
#                 if question_text:
#                     adjusted_answers = [answer.replace("-- THE END --", "").strip()

#                         for answer in answers

#                     ]
#                     output_structure["mc_questions"].append({
#                         "question": question_text,
#                         "answers": adjusted_answers
#                     })
#                 question_number = current_number
#                 question_text = question_match.group(2)
#                 answers = []
#             else:
#                 question_text += ' ' + line.strip()
#         elif re.match(r'^\s*[A-M]\.\s+.*', line):

#             answer = re.sub(r'^\s*[A-M]\.\s+', '', line).strip()

#             answers.append(escape_special_characters(answer))

#         elif re.match(r'^\s*[a-m]\.\s+.*', line):

#             answer = re.sub(r'^\s*[a-m]\.\s+', '', line).strip()

#             answers.append(escape_special_characters(answer))
#         else:
#             if answers:
#                 answers[-1] += '<br>' + escape_special_characters(line.strip())
#             else:
#                 question_text += '<br>' + '<br>'+ escape_special_characters(line.strip())


#     if question_text:
#         adjusted_answers = [

#             answer.replace("-- THE END --", "").strip()

#             for answer in answers

#         ]
#         output_structure["mc_questions"].append({
#             "question": question_text,
#             "answers": adjusted_answers
#         })

#     output_structured = reorder_answers(output_structure)

#     for question_info in output_structured["mc_questions"]:
#         question_info["question"] = clean_text(question_info["question"].lstrip('<br>'))

#         question_info["answers"] = [answer for answer in question_info["answers"]]

#         question_info["answers"] =  [re.sub(r'(?:<br>)+$', '', answer) for answer in  question_info["answers"]]

#         question_info["answers"] =  [clean_text(answer) for answer in  question_info["answers"]]

#     return json.dumps(output_structured, indent=4, ensure_ascii=False)
def reorder_answers(output_structure):
    for question_info in output_structure.values():
        for question in question_info:
            answers = question['answers']
            if answers:
                last_element = answers[-1].strip('<br>').strip()
                correct_answer_marker = last_element.split('\t')[-1].strip() if '\t' in last_element else last_element.split('<br>')[-1].strip()
                if correct_answer_marker:
                    correct_answer_label = correct_answer_marker[0].upper()
                    if 'a' <= correct_answer_label <= 'm' or 'A' <= correct_answer_label <= 'M':
                        correct_answer_index = ord(correct_answer_label.upper()) - ord('A')
                        if 0 <= correct_answer_index < len(answers):
                            correct_answer = answers.pop(correct_answer_index).replace(f'\t{correct_answer_label}', '').replace(f'<br>{correct_answer_label}', '')
                            answers.insert(0, correct_answer)
                            answers[-1] = answers[-1].replace(f'\t{correct_answer_label}', '').replace(f'<br>{correct_answer_label}', '')
                            answers[-1] = answers[-1].replace(f'\t{correct_answer_label.lower()}', '').replace(f'<br>{correct_answer_label.lower()}', '')
            else:
                print(f"No answers found for question: {question['question']}")

    return output_structure

def process_directory(directory):
    # Use the absolute path provided
    directory = os.path.abspath(directory)
    print(f"Processing directory: {directory}")
    
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return
    
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            txt_path = os.path.join(directory, filename)
            json_file_path = os.path.join(directory, os.path.splitext(filename)[0] + '.json')
            print(f"Processing file: {txt_path}")
            txt_to_json(txt_path, json_file_path, os.path.splitext(filename)[0])