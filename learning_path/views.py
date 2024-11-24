from django.shortcuts import render, redirect, get_object_or_404
from .models import LearningPath, Step
from .forms import LearningPathForm, StepForm

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from module_group.models import ModuleGroup


@login_required
def learning_path_list(request):
    learning_paths = LearningPath.objects.all()

    # Create a context with enrolled_count for each learning path
    learning_path_data = []
    for learning_path in learning_paths:
        enrolled_count = learning_path.enrolled_users.count()  # Count enrolled users
        learning_path_data.append({
            'learning_path': learning_path,
            'enrolled_count': enrolled_count,  # Include enrolled count in the data
        })

    module_groups = ModuleGroup.objects.all()
    return render(request, 'learning_path/list.html', 
        {
            'module_groups': module_groups,
            'learning_path_data': learning_path_data,
         
        })

@login_required
def enroll(request, learning_path_id):
    learning_path = get_object_or_404(LearningPath, pk=learning_path_id)

    if request.user not in learning_path.enrolled_users.all():
        learning_path.enrolled_users.add(request.user)
        # Increment recommended_count if needed
        learning_path.recommended_count += 1  # Increment count
        learning_path.save()  # Save changes to the database
        messages.success(request, f"You have successfully enrolled in {learning_path.title}.")
    else:
        messages.info(request, f"You are already enrolled in {learning_path.title}.")
    
    
    return redirect('learning_path:step_list', learning_path_id=learning_path.id)

@login_required
def duplicate(request, learning_path_id):
    original = get_object_or_404(LearningPath, pk=learning_path_id)
    
    # Create a copy of the original learning path
    new_learning_path = LearningPath.objects.create(
        title=f"Copy of {original.title}",
        description=original.description,
        creator=request.user,  # Optionally set the creator to the current user
        # Copy other necessary fields here
    )
    
    # Copy related steps and their associated courses
    for step in original.steps.all():
        # Create a new step instance
        new_step = Step(
            title=step.title,
            description=step.description,
            sequence=step.sequence,
            learning_path=new_learning_path  # Assign to the new path
        )
        new_step.save()  # Save the new step instance

        # Copy courses related to the original step
        for course in step.courses.all():
            new_step.courses.add(course)  # Associate courses with the new step

    messages.success(request, f"A duplicate of '{original.title}' has been created.")
    return redirect('learning_path:learning_path_list')


@login_required
def recommend(request, learning_path_id):
    learning_path = get_object_or_404(LearningPath, pk=learning_path_id)
    
    # Assuming there is a `recommend_count` field on the LearningPath model
    learning_path.recommended_count += 1
    learning_path.save()
    
    messages.success(request, f"You recommended '{learning_path.title}'!")
    return redirect('learning_path:step_list', learning_path_id=learning_path.id)


@login_required
def learning_path_edit(request, pk):
    learning_path = get_object_or_404(LearningPath, pk=pk)
    if request.method == 'POST':
        form = LearningPathForm(request.POST, instance=learning_path, user=request.user)  # Pass the current user
        if form.is_valid():
            form.save()
            return redirect('learning_path:learning_path_list')
    else:
        form = LearningPathForm(instance=learning_path, user=request.user)  # Pass the current user
    return render(request, 'learning_path/form.html', {'form': form})

@login_required
def learning_path_add(request):
    if request.method == 'POST':
        form = LearningPathForm(request.POST, user=request.user)  # Pass the current user
        if form.is_valid():
            form.save()
            return redirect('learning_path:learning_path_list')
    else:
        form = LearningPathForm(user=request.user)  # Pass the current user
    return render(request, 'learning_path/form.html', {'form': form})


@login_required
def learning_path_delete(request, pk):
    learning_path = get_object_or_404(LearningPath, pk=pk)
    if request.method == 'POST':
        learning_path.delete()
        return redirect('learning_path:learning_path_list')
    return render(request, 'learning_path/confirm_delete.html', {'learning_path': learning_path})

@login_required
def step_list(request, learning_path_id):
    # Retrieve the selected learning path and its steps
    learning_path = get_object_or_404(LearningPath, pk=learning_path_id)
    steps = learning_path.steps.all()
    
    # Retrieve all learning paths for the sidebar
    all_learning_paths = LearningPath.objects.all()
    
    return render(request, 'step/list.html', {
        'steps': steps,
        'learning_path': learning_path,
        'learning_paths': all_learning_paths  # Pass all learning paths for sidebar display
    })

@login_required
def step_add(request, learning_path_id):
    learning_path = get_object_or_404(LearningPath, pk=learning_path_id)
    if request.method == 'POST':
        form = StepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.learning_path = learning_path  # Assign the learning path to the step
            step.save()
            form.save_m2m()  # Save many-to-many relationships for courses
            return redirect('learning_path:step_list', learning_path_id=learning_path.id)
    else:
        form = StepForm()
    return render(request, 'step/form.html', {'form': form, 'learning_path': learning_path})

@login_required
def step_edit(request, learning_path_id, pk):
    step = get_object_or_404(Step, pk=pk)
    if request.method == 'POST':
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save(commit=False)  # Save without committing to handle M2M
            step.learning_path_id = learning_path_id  # Optional, ensure correct learning path
            step.save()
            form.save_m2m()  # Save M2M relationships after saving the instance
            return redirect('learning_path:step_list', learning_path_id=learning_path_id)
    else:
        form = StepForm(instance=step)
    return render(request, 'step/form.html', {'form': form, 'learning_path': step.learning_path})

@login_required
def step_delete(request, learning_path_id, pk):
    step = get_object_or_404(Step, pk=pk)
    if request.method == 'POST':
        step.delete()
        return redirect('learning_path:step_list', learning_path_id=learning_path_id)
    return render(request, 'step/confirm_delete.html', {'step': step})
