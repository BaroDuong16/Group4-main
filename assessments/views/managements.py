import json
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, urlencode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.views import View

from exercises.libs.submission import grade_submission, precheck

from ..models import *
from quiz.models import Question
from course.models import Course
from module_group.models import ModuleGroup
from exercises.models import Exercise, Submission

from ..forms import *

from .tokens import invite_token_generator  # Adjust the import path as necessary


class Assessment_list(View):
    @method_decorator(login_required)
    def get(self, request):
        courses = Course.objects.all().order_by('course_name')
        assessments = Assessment.objects.all().order_by('created_at')
        # Lọc quiz dựa trên subject được chọn
        selected_course = request.GET.get('course', '')
        # if selected_course:
        #     assessments = assessments.filter(course__id=selected_course)
        
        # Dynamically calculate exercise and question counts for each assessment
        assessments_with_counts = []
        for assessment in assessments:
            # Assuming you have related models for exercises and questions
            exercise_count = assessment.exercises.count()  # Assuming 'exercises' is a related field
            question_count = assessment.questions.count()  # Assuming 'questions' is a related field in exercises
            assessments_with_counts.append({
                'selected_course': selected_course,
                'assessment': assessment,
                'exercise_count': exercise_count,
                'question_count': question_count,
            })
        module_groups = ModuleGroup.objects.all()
        # Pass the assessments with their exercise and question counts to the template
        return render(request, 'assessment/assessment_list.html', {
            'module_groups': module_groups,
            'courses': courses,
            'assessments_with_counts': assessments_with_counts,
        })


class Assessment_create(View):
    @method_decorator(login_required)
    def get(self, request):
        query = request.GET.get('search', '')
        exercises = Exercise.objects.filter(title__icontains=query)  # Filter exercises based on search query
        questions = Question.objects.filter(question_text__icontains=query)  # Filter questions based on search query
    
        paginator = Paginator(exercises, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        form = AssessmentForm()
        
        return render(request, 'assessment/assessment_form.html', {
            'form': form,
            'exercises': exercises,
            'questions': questions,
            'page_obj': page_obj,
            'selected_exercises': [],  # Initially no exercises selected
            'selected_questions': [],  # Initially no questions selected
            'search': query
        })
    
    @method_decorator(login_required)
    def post(self, request):
        form = AssessmentForm(request.POST)
        selected_exercises = request.POST.getlist('selected_exercises')  # Get selected exercises from form
        selected_questions = request.POST.getlist('selected_questions')  # Get selected questions from the form
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()
            form.save_m2m()  # Save ManyToMany relationships

            # Add selected exercises to the assessment
            for exercise_id in selected_exercises:
                exercise = get_object_or_404(Exercise, id=exercise_id)
                assessment.exercises.add(exercise)  # Add the exercises to assessment

            # Add selected questions to the assessment
            for question_id in selected_questions:
                question = get_object_or_404(Question, id=question_id)
                print(question)
                assessment.questions.add(question)  # Add questions to the assessment

            messages.success(request, 'Assessment created successfully with exercises!')
            return redirect('assessment:assessment_list')
        

class Assessment_detail(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        assessment = get_object_or_404(Assessment, pk=pk)
        
        # Query invited candidates for this assessment
        invited_candidates = InvitedCandidate.objects.filter(assessment=assessment)
    
        # Query attempts from registered users
        registered_attempts = StudentAssessmentAttempt.objects.filter(assessment=assessment)
        
        # Query attempts from non-registered candidates
        # non_registered_attempts = NonRegisteredCandidateAttempt.objects.filter(assessment=assessment)

        return render(request, 'assessment/assessment_detail.html', {
            'assessment': assessment,
            'invited_candidates': invited_candidates,
            'registered_attempts': registered_attempts,
            # 'non_registered_attempts': non_registered_attempts,
        })

class Assessment_edit(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        assessment = get_object_or_404(Assessment, id=pk)
    
        # Fetch all available exercises and questions
        exercises = Exercise.objects.all()
        questions = Question.objects.all()
        
        # Fetch selected exercises and questions for the assessment
        selected_exercises = assessment.exercises.values_list('id', flat=True)
        print("selected_exercise is:  {selected_exercises}")
        # selected_questions = assessment.questions.values_list('id', flat=True)
        selected_question_ids = assessment.questions.values_list('id', flat=True)
        print("selected_question_ids is:  {selected_question_ids}")
        selected_questions = Question.objects.filter(id__in=selected_question_ids)  # Fetching the actual Question objects
        print(f"selected_questions is: {selected_questions}")
        # selected_questions = assessment.questions.all()  # Fetching selected Question objects
        form = AssessmentForm(instance=assessment)

        return render(request, 'assessment/assessment_form.html', {
            'form': form,
            'assessment': assessment,
            'exercises': exercises,
            'questions': questions,
            'selected_exercises': selected_exercises,
            'selected_questions': selected_questions, 
        })
    @method_decorator(login_required)
    def post(self, request, pk):
        assessment = get_object_or_404(Assessment, id=pk)

        form = AssessmentForm(request.POST, instance=assessment)
        
        if form.is_valid():
            form.save()
            print("-----------------")
            # Update associated exercises
            selected_exercise_ids = request.POST.getlist('selected_exercises')
            print(f"form after post.getlist exercise {selected_exercise_ids}")
            assessment.exercises.set(selected_exercise_ids)  # Update the associated exercises
            print(f"assessment is:  {assessment}")
            print(f"assessment is:  { assessment.exercises}")
            # Update associated questions from the selected questions in the HTML
            selected_question_ids = request.POST.get('selected_questions', '').split(',')
            print(f"selected_question_ids is {selected_question_ids}")
            selected_question_ids = [q_id for q_id in selected_question_ids if q_id]  # Filter out empty strings
            
            assessment.questions.set(selected_question_ids)  # Update the associated questions
            
            assessment.save()

            messages.success(request, 'The assessment has been successfully saved.')
            return redirect('assessment:assessment_list') 


class Assessment_Type_List_View(View):
    def get(self, request):
        assessment_types = AssessmentType.objects.all()
        return render(request, 'assessmenttype/assessment_type_list.html', {'assessment_types': assessment_types})

class Assessment_Type_Create_View(View):
    def get(self, request):
        form = AssessmentTypeForm()
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

    def post(self, request):
        form = AssessmentTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('assessment:assessment_type_list'))
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

class Assessment_Type_Update_View(View):
    def get(self, request, pk):
        assessment_type = get_object_or_404(AssessmentType, pk=pk)
        form = AssessmentTypeForm(instance=assessment_type)
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

    def post(self, request, pk):
        assessment_type = get_object_or_404(AssessmentType, pk=pk)
        form = AssessmentTypeForm(request.POST, instance=assessment_type)
        if form.is_valid():
            form.save()
            return redirect(reverse('assessment:assessment_type_list'))
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

class Assessment_Type_Delete_View(View):
    def post(self, request, pk):
        assessment_type = get_object_or_404(AssessmentType, pk=pk)
        assessment_type.delete()
        return redirect(reverse('assessment:assessment_type_list'))