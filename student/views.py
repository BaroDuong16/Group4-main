from django.shortcuts import render, redirect, get_object_or_404
from .models import Student
from .forms import StudentRegistrationForm

# View to list all students
def student_list(request):
    students = Student.objects.all()
    return render(request, 'students/student_list.html', {'students': students})

# View to register a new student
def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentRegistrationForm()
    return render(request, 'students/student_register.html', {'form': form})

# View to update a student's information
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentRegistrationForm(instance=student)
    return render(request, 'students/student_update.html', {'form': form})

# View to delete a student
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})
