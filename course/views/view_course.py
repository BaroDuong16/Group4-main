# views.py
from django.shortcuts import render, redirect
from course.models import Course, ReadingMaterial
from course.forms import ReadingMaterialForm
from django.contrib.auth.decorators import login_required

@login_required
def add_reading_material(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = ReadingMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            reading_material = form.save(commit=False)
            reading_material.course = course
            reading_material.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = ReadingMaterialForm()
    return render(request, 'material/add_reading_material.html', {'form': form, 'course': course})

@login_required
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    materials = course.readingmaterial_set.all()
    return render(request, 'material/course_detail.html', {'course': course, 'materials': materials})
