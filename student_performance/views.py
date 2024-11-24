from django.shortcuts import render, get_object_or_404, redirect
from .models import StudentPerformance
from .forms import StudentPerformanceForm

# User views
def student_performance_list(request):
    student_performances = StudentPerformance.objects.all()
    return render(request, 'student_performance_list.html', {'student_performances': student_performances})

def student_performance_detail(request, pk):
    student_performance = get_object_or_404(StudentPerformance, pk=pk)
    return render(request, 'student_performance_detail.html', {'student_performance': student_performance})

def student_performance_add(request):
    if request.method == 'POST':
        form = StudentPerformanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_performance:student_performance_list')
    else:
        form = StudentPerformanceForm()
    return render(request, 'student_performance_form.html', {'form': form})

def student_performance_edit(request, pk):
    student_performance = get_object_or_404(StudentPerformance, pk=pk)
    if request.method == 'POST':
        form = StudentPerformanceForm(request.POST, instance=student_performance)
        if form.is_valid():
            form.save()
            return redirect('student_performance:student_performance_list')
    else:
        form = StudentPerformanceForm(instance=student_performance)
    return render(request, 'student_performance_form.html', {'form': form})

def update_pk_values():
    records = StudentPerformance.objects.order_by('performance_id')

    # Cập nhật giá trị `performance_id` cho từng bản ghi
    for index, record in enumerate(records, start=1):
        record.performance_id = index
        record.save()

def student_performance_delete(request, pk):
    student_performance = get_object_or_404(StudentPerformance, pk=pk)
    if request.method == 'POST':
        student_performance.delete()
        return redirect('student_performance:student_performance_list')
    return render(request, 'student_performance_confirm_delete.html', {'student_performance': student_performance})


