# Function(s) for usage
import json
import pandas as pd
from .models import QuizBank, Answer
from django.contrib import messages

from_option_to_index = dict(list(zip(['a', 'b', 'c', 'd', 'e', 'f', 'g'], [i for i in range(0, 7)])))

def get_random(course_id:int, num_questions:int) -> list[dict]:
    '''
    Method for getting random question with their course_name and number of questions\n
    :Input:\n
    course_name: str\n 
    num_questions: int\n
    :Output:\n
    list_of_questions: list[dict]\n
    \n
    Output example: \n
    [
        {'question': 'abc', 'answer': ['A', 'B'], 'key': 'A'}, 
        {'question': 'abf', 'answer': ['A', 'B', 'C'], 'key': 'B'}
    ]
    '''
    from .models import Answer
    import random
    
    # try:
    #     question_queryset = Answer.objects.filter(question__course_name__name=f"{course_name}")
    #     if len(question_queryset) == 0:
    #         raise Exception
    # except:
    #     question_queryset = Answer.objects.filter(question__course_name__code=f"{course_name}")
    #     if len(question_queryset) == 0:
    #         raise Exception('The input course code or code name is invalid')

    question_queryset = Answer.objects.filter(question__course_id=course_id)
        

    questions_list = list() 

    for question in question_queryset:
        question_context = question.question.question_text

        question_dict = dict({
            'question':question_context,
            'answer':list(),
            'key':list(),
            'id':None,
            'question_type':question.question.question_type
        })
        
        question_dict['id'] = question.question.id
        question_dict['answer'].append(question.option_text)
        if question.is_correct:
            question_dict['key'].append(question.option_text)

        questions_list.append(question_dict)
    
    def merge_dictionaries(dictionaries):
        merged_dict = {}
        for dictionary in dictionaries:
            id = dictionary['id']
            question = dictionary['question']
            answer = dictionary['answer']
            key = dictionary['key']
            question_type = dictionary['question_type']

            if question not in merged_dict:
                merged_dict[question] = {'answer': [], 'key': list(), 'id':None}

            merged_dict[question]['answer'].extend(answer)
            merged_dict[question]['key'].extend(key)
            if id is not None:
                merged_dict[question]['id'] = id
            if question_type is not None:
                merged_dict[question]['question_type'] = question_type

        return list(merged_dict.items())

    questions_list = merge_dictionaries(questions_list)

    final_question_list = list()

    for question in questions_list:
        processed_question = (question[0], question[1]['answer'], question[1]['key'], question[1]['id'], question[1]['question_type'])
        final_question_list.append(dict(zip(["question", "options", "correct", "id", 'question_type'], processed_question)))

    random.shuffle(final_question_list)
    
    # if num_questions <= len(final_question_list):
    #     return str(final_question_list[:num_questions]).replace("'", '"')
    # else:
    #     return str(final_question_list).replace("'", '"')
    
    if num_questions <= len(final_question_list):
        return final_question_list[:num_questions]
    else:
        return final_question_list
    
def import_multiple_choice_question(request,
                                    df:pd.DataFrame,
                                    course_id:int):
    print('come here')
    for i, (index, row) in enumerate(df.iterrows()):
        options = [f'options[{i}]' for i in ['a', 'b', 'c', 'd', 'e', 'f', 'g']]
        question = str(row.get('question'))
        answer = pd.DataFrame(row.get(options))
        true_answer = str(row.get('correct')).split(',')
        # print(question, answer, true_answer, sep='\n')
        answer = answer.loc[answer[i] != '']
        answer_list = answer[i].to_list()
        transtated_key = [answer_list[from_option_to_index[option]] for option in true_answer]
        points = int(str(row.get('points')).strip())
        print(f"Processing question: {question}")

        if not QuizBank.objects.filter(question_text=question, course_id=course_id,question_type='MCQ').exists():
            # Create and save the new user
            QuizBank.objects.create(
                question_text=question,
                course_id=course_id,
                question_type='MCQ',
                points=points
            )
            print(f"Question {question} created")  # Debugging
        else:
            messages.warning(request, f"Question '{question}' already exists. Skipping.")
            print(f"Question {question} already exists")  # Debugging
        
        answer_list = [str(item) for item in answer_list]
        answer_list = list(map(lambda x : x.strip(), answer_list))
        transtated_key = [str(item) for item in transtated_key]
        key_list = [i in transtated_key for i in answer_list]

        question_id = QuizBank.objects.get(question_text=question, course_id=course_id).id
        for a, k in zip(answer_list, key_list):
            if not Answer.objects.filter(option_text=a, question_id=question_id).exists():
                # Create and save the new user
                Answer.objects.create(
                    option_text = a,
                    is_correct = k,
                    question_id=question_id
                )
                print(f"Answer {a} for question {question} created")  # Debugging
            else:
                messages.warning(request, f"Answer '{a}' for question {question} already exists. Skipping.")
                print(f"Answer {a} for question {question} already exists")  # Debugging

def import_true_false_question(request,
                                df:pd.DataFrame,
                                course_id:int):
    for i, (index, row) in enumerate(df.iterrows()):
        options = [f'options[{i}]' for i in ['a', 'b']]
        question = str(row.get('question'))
        answer = pd.DataFrame(row.get(options))
        true_answer = str(row.get('correct')).split(',')
        # print(question, answer, true_answer, sep='\n')
        answer = answer.loc[answer[i] != '']
        answer_list = answer[i].to_list()
        transtated_key = [answer_list[from_option_to_index[option]] for option in true_answer]
        points = int(str(row.get('points')).strip())
        print(f"Processing question: {question}")

        if not QuizBank.objects.filter(question_text=question, course_id=course_id,question_type='TF').exists():
            # Create and save the new user
            QuizBank.objects.create(
                question_text=question,
                course_id=course_id,
                question_type='TF',
                points=points
            )
            print(f"Question {question} created")  # Debugging
        else:
            messages.warning(request, f"Question '{question}' already exists. Skipping.")
            print(f"Question {question} already exists")  # Debugging
        
        answer_list = [str(item) for item in answer_list]
        answer_list = list(map(lambda x : x.strip(), answer_list))
        transtated_key = [str(item) for item in transtated_key]
        key_list = [i in transtated_key for i in answer_list]

        question_id = QuizBank.objects.get(question_text=question, course_id=course_id).id
        for a, k in zip(answer_list, key_list):
            if not Answer.objects.filter(option_text=a, question_id=question_id).exists():
                # Create and save the new user
                Answer.objects.create(
                    option_text = a,
                    is_correct = k,
                    question_id=question_id
                )
                print(f"Answer {a} for question {question} created")  # Debugging
            else:
                messages.warning(request, f"Answer '{a}' for question {question} already exists. Skipping.")
                print(f"Answer {a} for question {question} already exists")  # Debugging
                # IMPORTANT: insert code to create object to Answer HERE

def import_text_question(request,
                        df:pd.DataFrame,
                        course_id:int):
    for i, (index, row) in enumerate(df.iterrows()):
        question = str(row.get('question')).strip()
        true_answer = str(row.get('correct')).strip()
        points = int(str(row.get('points')).strip())
        print(f"Processing question: {question}")

        if not QuizBank.objects.filter(question_text=question, course_id=course_id,question_type='TEXT').exists():
            # Create and save the new user
            QuizBank.objects.create(
                question_text=question,
                course_id=course_id,
                question_type='TEXT',
                points=points
            )
            print(f"Question {question} created")  # Debugging
        else:
            messages.warning(request, f"Question '{question}' already exists. Skipping.")
            print(f"Question {question} already exists")  # Debugging

        question_id = QuizBank.objects.get(question_text=question, course_id=course_id).id
        if not Answer.objects.filter(option_text=true_answer, question_id=question_id).exists():
            # Create and save the new user
            Answer.objects.create(
                option_text = true_answer,
                is_correct = True,
                question_id=question_id
            )
            print(f"Answer {true_answer} for question {question} created")  # Debugging
        else:
            messages.warning(request, f"Answer '{true_answer}' for question {question} already exists. Skipping.")
            print(f"Answer {true_answer} for question {question} already exists")  # Debugging
            # IMPORTANT: insert code to create object to Answer HERE