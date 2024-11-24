from django.shortcuts import render, get_object_or_404, redirect
from training_program.models import TrainingProgram
from module_group.models import ModuleGroup
from user.models import User
from subject.models import Subject  # Ensure you import the Subject model

from .forms import TrainingProgramForm 

# Home view
def home(request):
    return render(request, 'home.html')

# Manage subjects in a training program
def manage_subjects(request, program_id):
    program = get_object_or_404(TrainingProgram, pk=program_id)

    all_subjects = Subject.objects.all()  # Get all available subjects
 
    if request.method == 'POST':
        # Update the program's subjects
        selected_subjects = request.POST.getlist('subjects')  # Get selected subjects from the form
        program.subjects.set(selected_subjects)  # Update the ManyToMany relationship
        return redirect('training_program:training_program_list')
    
    return render(request, 'manage_subjects.html', {
        'program': program,
        'all_subjects': all_subjects,
        'selected_subjects': program.subjects.all(),  # Pass the currently selected subjects
    })

# TrainingProgram views
def training_program_list(request):
    module_groups = ModuleGroup.objects.all()
    programs = TrainingProgram.objects.all()
    return render(request, 'training_program_list.html', {
        'programs': programs,
        'module_groups': module_groups,
    })

def training_program_add(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('training_program:training_program_list')
    else:
        form = TrainingProgramForm()
    return render(request, 'training_program_form.html', {'form': form})

def training_program_edit(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('training_program:training_program_list')
    else:
        form = TrainingProgramForm(instance=program)
    return render(request, 'training_program_form.html', {'form': form})

def training_program_delete(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        program.delete()
        return redirect('training_program:training_program_list')
    return render(request, 'training_program_confirm_delete.html', {'program': program})
