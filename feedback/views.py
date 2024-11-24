from django.shortcuts import render, redirect, get_object_or_404
from .forms import InstructorFeedbackForm, CourseFeedbackForm, TrainingProgramFeedbackForm
from .models import InstructorFeedback, CourseFeedback, TrainingProgramFeedback
from course.models import Course
from training_program.models import TrainingProgram
from django.contrib.auth import get_user_model
from module_group.models import ModuleGroup, Module
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, FloatField, ExpressionWrapper, Count
from django.http import Http404

'''def feedback_list(request):
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    instructor_feedbacks = InstructorFeedback.objects.all()
    course_feedbacks = CourseFeedback.objects.all()
    training_feedbacks = TrainingProgramFeedback.objects.all()

    return render(request, 'feedback_list.html', {
        'instructor_feedbacks': instructor_feedbacks,
        'course_feedbacks': course_feedbacks,
        'training_feedbacks': training_feedbacks,
        'module_groups': module_groups,
        'modules': modules
    })'''

User = get_user_model()

def feedback_list(request):
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    instructor_feedbacks = InstructorFeedback.objects.all()
    course_feedbacks = CourseFeedback.objects.all()
    training_feedbacks = TrainingProgramFeedback.objects.all()

    # Fetch instructors and courses
    instructors = User.objects.filter(id__in=Course.objects.values_list('instructor_id', flat=True)).distinct()  # Assuming you have a role model for instructors
    courses = Course.objects.all()
    training_programs = TrainingProgram.objects.all()

    return render(request, 'feedback_list.html', {
        'instructor_feedbacks': instructor_feedbacks,
        'course_feedbacks': course_feedbacks,
        'training_feedbacks': training_feedbacks,
        'module_groups': module_groups,
        'modules': modules,
        'instructors': instructors,
        'courses': courses,
        'training_programs': training_programs  # Add training programs as well
    })

def give_instructor_feedback(request, instructor_id):
    instructor = User.objects.get(pk=instructor_id)
    if request.method == 'POST':
        form = InstructorFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.instructor = instructor
            feedback.save()
            return redirect('feedback:feedback_success')
    else:
        form = InstructorFeedbackForm()
    return render(request, 'feedback_Instructor.html', {'form': form, 'instructor': instructor})

def give_course_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.course = course
            feedback.save()
            messages.success(request, 'Your feedback has been submitted successfully.')
            return redirect('course:course_detail', pk=course.id)
        else:
            messages.error(request, 'There was an error with your submission. Please check the form and try again.')
    else:
        form = CourseFeedbackForm()

    # Fetch the 5 newest feedback entries for this course
    latest_feedbacks = CourseFeedback.objects.filter(course=course).order_by('-created_at')[:5]

    return render(request, 'feedback_Course.html', {
        'form': form,
        'course': course,
        'latest_feedbacks': latest_feedbacks
    })

def give_training_program_feedback(request, training_program_id):
    training_program = TrainingProgram.objects.get(pk=training_program_id)
    if request.method == 'POST':
        form = TrainingProgramFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.training_program = training_program
            feedback.save()
            return redirect('feedback:feedback_success')
    else:
        form = TrainingProgramFeedbackForm()
    return render(request, 'feedback_Program.html', {'form': form, 'training_program': training_program})

def feedback_success(request):
    return render(request, 'feedback_success.html')

def instructor_feedback_detail(request, feedback_id):
    feedback = InstructorFeedback.objects.get(pk=feedback_id)
    return render(request, 'feedback_detail.html', {'feedback': feedback, 'type': 'Instructor'})

def course_feedback_detail(request, feedback_id):
    feedback = CourseFeedback.objects.get(pk=feedback_id)
    return render(request, 'feedback_detail.html', {'feedback': feedback, 'type': 'Course'})

def program_feedback_detail(request, feedback_id):
    try:
        feedback = TrainingProgramFeedback.objects.get(pk=feedback_id)
    except TrainingProgramFeedback.DoesNotExist:
        raise Http404("Feedback does not exist")
    return render(request, 'feedback_detail.html', {'feedback': feedback, 'type': 'Training Program'})

def course_all_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    all_feedbacks = CourseFeedback.objects.filter(course=course)

    # Calculate rating distribution
    total_feedbacks = all_feedbacks.count()
    rating_distribution = []

    if total_feedbacks > 0: #31/10
        for rating in range(5, 0,-1):  # 5 to 1 in reverse order
            count = len([f for f in all_feedbacks if (f.average_rating() - rating) < 1 and (f.average_rating() - rating) >= 0])
            percentage = (count / total_feedbacks) * 100
            rating_distribution.append({
                'rating': rating,
                'count': count,
                'percentage': percentage
            })

        # Calculate overall average rating
        total_rating = sum(feedback.average_rating() for feedback in all_feedbacks)
        course_average_rating = total_rating / total_feedbacks
        course_average_rating_star = course_average_rating * 20  # Convert to percentage (0-100)
    else:
        course_average_rating = None
        course_average_rating_star = 0
        rating_distribution = [{'rating': i, 'count': 0, 'percentage': 0} for i in range(5, 0, -1)]

    sort_by = request.GET.get('sort', 'recent')
    all_feedbacks = all_feedbacks.annotate(helpful_count=Count('helpful_rate'))

    if sort_by == 'helpful':
        all_feedbacks = all_feedbacks.order_by('-helpful_count', '-created_at')
    else:
        all_feedbacks = all_feedbacks.order_by('-created_at')

    selected_rating = request.GET.get('rating', None)

    all_feedbacks = all_feedbacks.annotate(
        average_rating=ExpressionWrapper(
            (F('course_material') + F('clarity_of_explanation') +
             F('course_structure') + F('practical_applications') +
             F('support_materials')) / 5.0,
            output_field=FloatField()
        )
    )

    if selected_rating:
        try:
            selected_rating = int(selected_rating)
            all_feedbacks = all_feedbacks.filter(average_rating__gte=selected_rating,
                                               average_rating__lt=selected_rating + 1).order_by('-created_at')
        except ValueError:
            pass

    paginator = Paginator(all_feedbacks, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'feedback_course_list.html', {
        'course': course,
        'page_obj': page_obj,
        'course_average_rating': course_average_rating,
        'course_average_rating_star': course_average_rating_star,
        'range': {1,2,3,4,5},
        'selected_rating': selected_rating,
        'sort_by': sort_by,
        'total_feedbacks': total_feedbacks,
        'rating_distribution': rating_distribution,  # Added this to the context
    })

def helpful_rate(request, pk):
    feedback = get_object_or_404(CourseFeedback, pk=pk)
    print(feedback.id)
    if request.user in feedback.helpful_rate.all():
        feedback.helpful_rate.remove(request.user)
    else:
        feedback.helpful_rate.add(request.user)
    return redirect('feedback:course_all_feedback', course_id=feedback.course.id)
