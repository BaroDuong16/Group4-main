# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from course.models import Course, Enrollment, Session, CourseMaterial, ReadingMaterial, Completion, SessionCompletion
from student_portal.models import RecommendedCourse
from django.contrib import messages
from feedback.models import CourseFeedback
import random
from django.utils import timezone  # for timestamp updates
from django.core.paginator import Paginator
from user.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

@login_required
def course_content(request, pk, session_id=None):
    course = get_object_or_404(Course, pk=pk)
    sessions = Session.objects.filter(course=course).order_by('order')

    # Select the first session if no session_id is provided
    selected_session_id = session_id or request.POST.get('session_id') or sessions.first().id if sessions.exists() else None

    # Get the current session or default to the first available session
    current_session = get_object_or_404(Session, id=selected_session_id) if selected_session_id else None
    materials = CourseMaterial.objects.filter(session=current_session).order_by('order') if current_session else []

    # Handle material selection and default to the first material if none specified
    file_id = request.GET.get('file_id')
    file_type = request.GET.get('file_type')
    if file_id and file_type and current_session:
        current_material = CourseMaterial.objects.filter(id=file_id, material_type=file_type, session=current_session).first()
    else:
        current_material = materials.first() if materials.exists() else None

    # Determine the next material and session for navigation
    next_material = materials.filter(order__gt=current_material.order).first() if current_material else None
    next_session = None
    if not next_material and current_session:
        next_session = Session.objects.filter(course=course, order__gt=current_session.order).order_by('order').first()
        next_material = CourseMaterial.objects.filter(session=next_session).order_by('order').first() if next_session else None

    # Determine content type and preview content
    content_type = None
    preview_content = None
    if current_material:
        reading = ReadingMaterial.objects.filter(material_id=current_material.id).first()
        if reading:
            preview_content = reading.content
            content_type = current_material.material_type

    # Completion status for the current material
    completion_status = (
        Completion.objects.filter(
            session=current_session,
            material=current_material,
            user=request.user,
            completed=True
        ).exists() if current_material else False
    )

    # Calculate course completion percentage
    total_materials = CourseMaterial.objects.filter(session__course=course).count()
    completed_materials = Completion.objects.filter(session__course=course, user=request.user, completed=True).count()
    completion_percent = (completed_materials / total_materials) * 100 if total_materials > 0 else 0

    # Check if user is eligible for a certificate
    total_sessions = sessions.count()
    completed_sessions = SessionCompletion.objects.filter(course=course, user=request.user, completed=True).count()
    certificate_url = (
        reverse('course:generate_certificate', kwargs={'pk': course.pk})
        if total_sessions > 0 and completed_sessions == total_sessions
        else None
    )

    context = {
        'course': course,
        'sessions': sessions,
        'current_session': current_session,
        'materials': materials,
        'current_material': current_material,
        'next_material': next_material,
        'content_type': content_type,
        'preview_content': preview_content,
        'completion_status': completion_status,
        'completion_percent': completion_percent,
        'certificate_url': certificate_url,
        'next_session': next_session,
    }

    return render(request, 'courses/course_content.html', context)


@require_POST
@login_required
def toggle_completion(request, pk):
    course = get_object_or_404(Course, pk=pk)
    file_id = request.POST.get('file_id')

    material = get_object_or_404(CourseMaterial, id=file_id, session__course=course)
    session = material.session

    completion, created = Completion.objects.get_or_create(
        session=session,
        material=material,
        user=request.user,
    )
    completion.completed = not completion.completed
    completion.save()

    # Check if all materials in the session are completed
    total_materials = session.materials.count()
    completed_materials = Completion.objects.filter(session=session, user=request.user, completed=True).count()
    session_completed = total_materials == completed_materials

    SessionCompletion.objects.update_or_create(
        user=request.user,
        session=session,
        course=course,
        defaults={'completed': session_completed}
    )

    # Find the next item
    next_material = CourseMaterial.objects.filter(
        session=session,
        order__gt=material.order
    ).order_by('order').first()

    next_session = None
    if not next_material:
        next_session = Session.objects.filter(course=course, order__gt=session.order).order_by('order').first()
        if next_session:
            next_material = CourseMaterial.objects.filter(session=next_session).order_by('order').first()

    next_item_type = next_material.material_type if next_material else None
    next_item_id = next_material.id if next_material else None
    next_session_id = next_session.id if next_session else None

    return JsonResponse({
        'completed': completion.completed,
        'next_item_type': next_item_type,
        'next_item_id': next_item_id,
        'next_session_id': next_session_id
    })
# @login_required
# def course_list(request):
#     # Retrieve all published courses initially
#     courses = Course.objects.filter(published=True)
#     query = request.GET.get('q')
    
#     # Fetch enrolled courses for the student
#     enrolled_courses = Enrollment.objects.filter(student=request.user).values_list('course', flat=True)
#     enrolled_courses_list = Course.objects.filter(id__in=enrolled_courses, published=True)
    
#     # If a search query is present, filter the courses based on the search
#     if query:
#         courses = courses.filter(Q(course_name__icontains=query) | Q(description__icontains=query))
#         enrolled_courses_list = enrolled_courses_list.filter(Q(course_name__icontains=query) | Q(description__icontains=query))
    
#     # Combine enrolled courses with other filtered courses, removing duplicates
#     courses = list(enrolled_courses_list) + [course for course in courses if course not in enrolled_courses_list]

#     # Add average rating to each course
#     for course in courses:
#         feedbacks = course.coursefeedback_set.all()
#         if feedbacks.exists():
#             total_ratings = sum(feedback.average_rating() for feedback in feedbacks)
#             course.average_rating = total_ratings / feedbacks.count()
#         else:
#             course.average_rating = 0.0  # Default to 0 if no feedbacks

#     # Insert or update recommended courses based on search results
#     for course in courses:
#         recommended_course, created = RecommendedCourse.objects.get_or_create(
#             course=course,
#             user=request.user,  # Associate with the logged-in user
#             defaults={'created_at': timezone.now()}
#         )
#         if not created:
#             recommended_course.created_at = timezone.now()
#             recommended_course.save()

#     # Pagination setup
#     paginator = Paginator(courses, 6)  # Show 6 courses per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # Get top recommended courses to display
#     recommended_courses = RecommendedCourse.objects.filter(course__published=True).order_by('-created_at')[:4]

#     # Render the course list with filtered and recommended courses
#     return render(request, 'courses/course_list.html', {
#         'courses': page_obj,
#         'recommended_courses': [rc.course for rc in recommended_courses],
#     })


def course_list(request): 
    # Retrieve all published courses
    courses = Course.objects.filter(published=True)
    query = request.GET.get('q')
    
    # Fetch enrolled courses for the student
    enrolled_course_ids = Enrollment.objects.filter(student=request.user).values_list('course', flat=True)
    enrolled_courses_list = Course.objects.filter(id__in=enrolled_course_ids, published=True)
    
    # If a search query is present, filter the courses
    if query:
        courses = courses.filter(Q(course_name__icontains=query) | Q(description__icontains=query))
        enrolled_courses_list = enrolled_courses_list.filter(Q(course_name__icontains=query) | Q(description__icontains=query))
    
    # Combine enrolled courses with other filtered courses, removing duplicates
    courses = list(enrolled_courses_list) + [course for course in courses if course not in enrolled_courses_list]

    # Mark courses as enrolled or not
    for course in courses:
        course.user_enrolled = course.id in enrolled_course_ids

        # Calculate the average rating for each course
        feedbacks = course.coursefeedback_set.all()
        if feedbacks.exists():
            total_ratings = sum(feedback.average_rating() for feedback in feedbacks)
            course.average_rating = total_ratings / feedbacks.count()
        else:
            course.average_rating = 0.0

    # Insert or update recommended courses
    for course in courses:
        recommended_course, created = RecommendedCourse.objects.get_or_create(
            course=course,
            user=request.user,
            defaults={'created_at': timezone.now()}
        )
        if not created:
            recommended_course.created_at = timezone.now()
            recommended_course.save()

    # Pagination setup
    paginator = Paginator(courses, 6)  # Show 6 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get top recommended courses
    recommended_courses = RecommendedCourse.objects.filter(course__published=True).order_by('-created_at')[:4]

    # Render the course list with filtered and recommended courses
    return render(request, 'courses/course_list.html', {
        'courses': page_obj,
        'recommended_courses': [rc.course for rc in recommended_courses],
    })

@login_required
def course_detail(request, pk):
    # Get the course based on the primary key (pk)
    course = get_object_or_404(Course, pk=pk)

    # Check enrollment status
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    users_enrolled_count = Enrollment.objects.filter(course=course).count()

    # Get all feedback related to the course
    feedbacks = CourseFeedback.objects.filter(course=course)

    # Calculate the course's average rating
    if feedbacks.exists():
        total_rating = sum(feedback.average_rating() for feedback in feedbacks)
        course_average_rating = total_rating / feedbacks.count()
    else:
        course_average_rating = None  # No feedback yet

    course_average_rating_star = course_average_rating * 100 / 5 if course_average_rating is not None else 0

    # Get prerequisites
    prerequisites = course.prerequisites.all()

    # Get sessions
    sessions = Session.objects.filter(course=course)
    session_count = sessions.count()

    # Get random tags
    all_tags = list(course.tags.all())
    random_tags = random.sample(all_tags, min(4, len(all_tags)))

    # Fetch the latest feedbacks
    latest_feedbacks = feedbacks.order_by('-created_at')[:5]

    # Instructor info
    instructor = course.instructor
    is_instructor = Course.objects.filter(instructor=request.user).exists()
    user_type = 'instructor' if is_instructor else 'student'

    enrolled_users = Enrollment.objects.filter(course=course).select_related('student')

    # Calculate progress for each enrolled user
    user_progress = [
        {
            'user': enrollment.student,
            'progress': course.get_completion_percent(enrollment.student)
        }
        for enrollment in enrolled_users
    ]

    context = {
        'course': course,
        'prerequisites': prerequisites,
        'is_enrolled': is_enrolled,
        'users_enrolled_count': users_enrolled_count,
        'course_average_rating_star': course_average_rating_star,
        'course_average_rating': course_average_rating,
        'feedbacks': feedbacks,
        'sessions': sessions,
        'session_count': session_count,
        'latest_feedbacks': latest_feedbacks,
        'tags': course.tags.all() if course.tags else [],
        'instructor': instructor,
        'user_type': user_type,
        'user_progress': user_progress,
        'random_tags': random_tags,
    }

    return render(request, 'courses/course_detail.html', context)


@login_required
def course_content2(request, pk):
    print('come here')
    
    # Retrieve the course by primary key
    course = get_object_or_404(Course, pk=pk)
    print(course)
    
    print('ab=')
    # Retrieve all sessions for this course, ordered by 'order'
    sessions = Session.objects.filter(course=course)

    print(sessions)
    # Attempt to get `session_id` from POST; if not present, it's set to None
    selected_session_id = request.POST.get('session_id') or None
    
    # Determine the current session based on `session_id` or default to the first session
    if selected_session_id:
        # If session_id is provided, try to retrieve the session
        current_session = get_object_or_404(Session, id=selected_session_id, course=course)
    else:
        # If no session_id is provided, default to the first session in the list
        current_session = sessions.first() if sessions.exists() else None

    # If there is no current session (e.g., no sessions found), handle this case appropriately
    if current_session is None:
        # Redirect to an error page or show a message if needed
        return render(request, 'courses/error.html', {'message': 'No sessions available for this course.'})
    
    # Retrieve course materials for the current session
    materials = CourseMaterial.objects.filter(session=current_session).order_by('order')

    file_id = request.GET.get('file_id')
    file_type = request.GET.get('file_type')
    current_material = None
    if file_id and file_type:
        try:
            current_material = CourseMaterial.objects.get(id=file_id, material_type=file_type, session=current_session)
        except CourseMaterial.DoesNotExist:
            current_material = materials.first() if materials.exists() else None
    else:
        current_material = materials.first() if materials.exists() else None

    next_material = materials.filter(order__gt=current_material.order).first() if current_material else None
    next_session = None

    if not next_material:
        next_session = Session.objects.filter(course=course, order__gt=current_session.order).order_by('order').first()
        if next_session:
            next_material = CourseMaterial.objects.filter(session=next_session).order_by('order').first()

    content_type = None
    preview_content = None

    if current_material:
        if current_material.material_type == 'assignments':
            reading = ReadingMaterial.objects.get(material_id=current_material.id)
            preview_content = reading.content
            content_type = 'assignments'
        elif current_material.material_type == 'labs':
            reading = ReadingMaterial.objects.get(material_id=current_material.id)
            preview_content = reading.content
            content_type = 'labs'
        elif current_material.material_type == 'lectures':
            reading = ReadingMaterial.objects.get(material_id=current_material.id)
            preview_content = reading.content
            content_type = 'lectures'
        elif current_material.material_type == 'references':
            reading = ReadingMaterial.objects.get(material_id=current_material.id)
            preview_content = reading.content
            content_type = 'references'

    completion_status = Completion.objects.filter(
        session=current_session,
        material=current_material,
        user=request.user,
        completed=True
    ).exists() if current_material else False

    total_materials = CourseMaterial.objects.filter(session__course=course).count()
    completed_materials = Completion.objects.filter(
        session__course=course,
        user=request.user,
        completed=True
    ).count()
    completion_percent = (completed_materials / total_materials) * 100 if total_materials > 0 else 0

    total_sessions = sessions.count()
    completed_sessions = SessionCompletion.objects.filter(course=course, user=request.user, completed=True).count()

    certificate_url = None
    if total_sessions > 0 and completed_sessions == total_sessions:
        # Call the function to generate the certificate URL
        certificate_url = reverse('courses:generate_certificate', kwargs={'pk': course.pk})

    context = {
        'course': course,
        'sessions': sessions,
        'current_session': current_session,
        'materials': materials,
        'current_material': current_material,
        'next_material': next_material,
        'content_type': content_type,
        'preview_content': preview_content,
        'completion_status': completion_status,
        'completion_percent': completion_percent,
        'certificate_url': certificate_url,
        'next_session': next_session,
    }

    return render(request, 'courses/course_content.html', context)

@login_required
def instructor_profile(request, instructor_id):
    # Get the instructor based on the instructor ID
    instructor = get_object_or_404(User, id=instructor_id)

    # Get courses taught by this instructor
    courses = Course.objects.filter(instructor=instructor)

    # Get feedback for each course to calculate average ratings
    for course in courses:
        feedbacks = CourseFeedback.objects.filter(course=course)
        if feedbacks.exists():
            total_rating = sum(feedback.average_rating() for feedback in feedbacks)
            course.average_rating = total_rating / feedbacks.count()
        else:
            course.average_rating = None  # No feedback yet

    context = {
        'instructor': instructor,
        'courses': courses,
    }

    return render(request, 'instructor_profile.html', context)

@login_required
def enroll(request, pk):
    course = get_object_or_404(Course, id=pk)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f"You have successfully enrolled in {course.course_name}.")
    return redirect('student_portal:course_detail', pk=course.id)

@login_required
def unenroll(request, pk):
    # Get the course based on the primary key (pk)
    course = get_object_or_404(Course, pk=pk)

    # Attempt to delete the enrollment for the current user
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    
    if enrollment:
        enrollment.delete()
        messages.success(request, f"You have successfully unenrolled from {course.course_name}.")
    else:
        messages.warning(request, f"You are not enrolled in {course.course_name}.")

    return redirect('student_portal:course_detail', pk=course.pk)
