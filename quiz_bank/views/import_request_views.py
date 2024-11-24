from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from quiz.models import Quiz, Question, AnswerOption
from course.models import Course
from copy import deepcopy
import json
import pandas as pd
from ..models import QuizBank, Answer
from ..functions import *
from ..forms import *
from django.contrib import messages

def import_quiz_bank(request):
    if request.method == 'POST':
        # print(dict(request))
        excel_form = ExcelImportForm(request.POST, request.FILES)
        if excel_form.is_valid():
            uploaded_file = request.FILES['excel_file']
            course_name = excel_form.cleaned_data['course']
            question_type = excel_form.cleaned_data['question_type']
            print(course_name)
            try:
                try:
                    course_id = Course.objects.get(course_name=course_name).id
                except:
                    course_id = Course.objects.get(course_code=course_name).id
            except:
                return redirect(reverse('quiz_bank:quiz_bank_view'))
            try:
                # Read the Excel file
                # df = pd.read_excel(uploaded_file)
                # df.fillna('', inplace=True)
                df = pd.read_excel(uploaded_file)

                # Identify option columns and convert them to 'object' type
                option_columns = [col for col in df.columns if 'options' in col]
                df[option_columns] = df[option_columns].astype('object')

                # Fill NaN values with empty strings in the option columns
                df[option_columns] = df[option_columns].fillna('')
                # Loop over the rows in the DataFrame
                match (question_type):
                    case 'MCQ':
                        import_multiple_choice_question(request, df, course_id)
                    case 'TF':
                        import_true_false_question(request, df, course_id)
                    case 'TEXT':
                        import_text_question(request, df, course_id)

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect('quiz_bank:quiz_bank_view')
    else:
        excel_form = ExcelImportForm()

    return render(request, 'quiz_bank_view.html', {'excel_form': excel_form})

def import_quiz_bank_from_page(request, course_id):
    if request.method == 'POST':
        # print(dict(request))
        excel_form = ExcelImportWithoutCourseForm(request.POST, request.FILES)
        if excel_form.is_valid():
            uploaded_file = request.FILES['excel_file']
            question_type = excel_form.cleaned_data['question_type']
            try:
                # Read the Excel file
                df = pd.read_excel(uploaded_file)

                # Identify option columns and convert them to 'object' type
                option_columns = [col for col in df.columns if 'options' in col]
                df[option_columns] = df[option_columns].astype('object')

                # Fill NaN values with empty strings in the option columns
                df[option_columns] = df[option_columns].fillna('')

                # # Convert all columns to object type (string-compatible) before filling NaN values
                # df = df.astype({col: 'object' for col in df.columns})
                # df.fillna('', inplace=True)

                # Loop over the rows in the DataFrame
                print(question_type)
                match (question_type):
                    case 'MCQ':
                        print('mqc')
                        import_multiple_choice_question(request, df, course_id)
                    case 'TF':
                        import_true_false_question(request, df, course_id)
                    case 'TEXT':
                        import_text_question(request, df, course_id)

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect(reverse('quiz_bank:quiz_bank_course', kwargs={'course_id':course_id}))
    else:
        excel_form = ExcelImportWithoutCourseForm()

    return render(request, 'quiz_bank_course.html', {'excel_form': excel_form})