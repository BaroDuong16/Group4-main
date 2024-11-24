from django.shortcuts import render,get_object_or_404,redirect
from .models import Assignment
from .forms import AssignmentForm

# Create your views here.
def assignment_list(request):
    assignments = Assignment.objects.all()
    return render(request, 'assignment_list.html', {'assignments': assignments})

def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'assignment_detail.html', {'assignment': assignment})

def assignment_add(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            return redirect('assignment:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm()
    return render(request, 'assignment_form.html', {'form': form})

def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            return redirect('assignment:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'assignment_form.html', {'form': form})

def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        return redirect('assignment:assignment_list')
    return render(request, 'assignment_confirm_delete.html', {'assignment': assignment})

