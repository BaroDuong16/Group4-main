# enrollment/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import EnrollmentForm, AdminEnrollmentForm
from course.models import Enrollment, Course
from django.contrib.auth.decorators import user_passes_test
from collaboration_group.models import CollaborationGroup, GroupMember
from django.db import IntegrityError
from module_group.models import ModuleGroup
from django.http import JsonResponse

def fetch_enrolled_users(request):
    course_id = request.GET.get('course_id')
    selected_group_id = request.GET.get('group_id')
    enrolled_users = Enrollment.objects.filter(course_id=course_id).values_list('student_id', flat=True)
    
    # Get all users in the selected group
    group_users = GroupMember.objects.filter(group_id=selected_group_id).select_related('user')
    
    # Prepare JSON response with enrollment status
    users_data = [
        {
            "user_id": member.user.id,
            "username": member.user.username,
            "email": member.user.email,
            "is_enrolled": member.user.id in enrolled_users
        }
        for member in group_users
    ]
    return JsonResponse(users_data, safe=False)


@user_passes_test(lambda u: u.is_superuser)  # Restrict access to superusers only
def enrollment_list(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    print(enrollments)
    all_enrollments = Enrollment.objects.all()  # Fetch all enrollments for admin view
    module_groups = ModuleGroup.objects.all()
    
    return render(request, 'enrollment/enrollment_list.html', {
        'module_groups': module_groups,
        'enrollments': enrollments,
        'all_enrollments': all_enrollments,
    })


def admin_enroll_users(request):
    groups = CollaborationGroup.objects.all()
    courses = Course.objects.filter(published=True)
    selected_group_id = request.GET.get('group')
    selected_course_id = request.GET.get('course') or (request.POST.get('course') if request.method == 'POST' else None)
    group_members = []
    enrolled_users = []

    if selected_group_id:
        # Fetch members of the selected group with user details
        group_members = GroupMember.objects.filter(group_id=selected_group_id).select_related('user')

        if selected_course_id:
            # Fetch enrolled users for the selected course and group
            enrolled_users = Enrollment.objects.filter(course_id=selected_course_id).values_list('student_id', flat=True)

    if request.method == 'POST':
        selected_users = request.POST.getlist('users')
        course_id = request.POST.get('course')

        if selected_users and course_id:
            for user_id in selected_users:
                try:
                    Enrollment.objects.create(student_id=user_id, course_id=course_id)
                except IntegrityError:
                    messages.warning(request, f"User ID {user_id} is already enrolled in this course.")
            messages.success(request, "Selected users have been enrolled successfully.")
            
        # Redirect with selected group and course to retain selection
        return redirect(f"{request.path}?group={selected_group_id}&course={selected_course_id}")

    return render(request, 'enrollment/admin_enroll_users.html', {
        'groups': groups,
        'selected_group_id': selected_group_id,
        'selected_course_id': selected_course_id,
        'group_members': group_members,
        'courses': courses,
        'enrolled_users': enrolled_users,
    })


def enroll_student(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, user=request.user)  # Pass user for filtering
        if form.is_valid():
            course = form.cleaned_data['course']
            # Check if the student is already enrolled in this course
            if Enrollment.objects.filter(student=request.user, course=course).exists():
                messages.error(request, f'You are already enrolled in {course.course_name}.')
            else:
                # Enroll student since they are not already enrolled
                enrollment = form.save(commit=False)
                enrollment.student = request.user
                enrollment.save()
                messages.success(request, f'You have successfully enrolled in {course.course_name}.')
            # Render the enrollment list with messages showing immediately
            return redirect('group_enrollment:enrollment_list')
    else:
        form = EnrollmentForm(user=request.user)  # Pass user for filtering

    # Render the same template with the form to show validation or success messages
    return render(request, 'enrollment/enroll_student.html', {'form': form})

# def enrollment_list(request):
#     enrollments = Enrollment.objects.filter(student=request.user)
#     return render(request, 'enrollment/enrollment_list.html', {'enrollments': enrollments})

def edit_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Enrollment for {enrollment.course.course_name} updated successfully.')
            return redirect('enrollment:enrollment_list')
    else:
        form = EnrollmentForm(instance=enrollment)

    return render(request, 'enrollment/enroll_student.html', {'form': form})

def delete_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    enrollment.delete()
    messages.success(request, f'Enrollment for {enrollment.course.course_name} deleted successfully.')
    return redirect('enrollment:enrollment_list')
