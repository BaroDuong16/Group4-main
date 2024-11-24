from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import CollaborationGroupForm, GroupMemberForm
from .models import CollaborationGroup, GroupMember

User = get_user_model()

@login_required
def collaboration_group_list(request):
    collaboration_groups = CollaborationGroup.objects.all()

    if request.user.is_superuser:
        return render(request, 'admin_collaboration_group_list.html', {
            'collaboration_groups': collaboration_groups
        })

    return render(request, 'collaboration_group_list.html', {
        'collaboration_groups': collaboration_groups
    })

@login_required
def join_group(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)
    
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        GroupMember.objects.create(group=group, user=request.user)

    return redirect('collaboration_group:check_members', group_id=group.id)

@login_required
def collaboration_group_add(request):
    if request.method == 'POST':
        form = CollaborationGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('collaboration_group:collaboration_group_list')
    else:
        form = CollaborationGroupForm()
    return render(request, 'collaboration_group_form.html', {'form': form})

@login_required
def collaboration_group_edit(request, pk):
    collaboration_group = get_object_or_404(CollaborationGroup, pk=pk)

    if not (request.user == collaboration_group.created_by or request.user.is_superuser):
        return redirect('collaboration_group:collaboration_group_list')
    
    if request.method == 'POST':
        form = CollaborationGroupForm(request.POST, instance=collaboration_group)
        if form.is_valid():
            form.save()
            return redirect('collaboration_group:collaboration_group_list')
    else:
        form = CollaborationGroupForm(instance=collaboration_group)
    return render(request, 'collaboration_group_form.html', {'form': form})

@login_required
def collaboration_group_delete(request, pk):
    collaboration_group = get_object_or_404(CollaborationGroup, pk=pk)
    
    if collaboration_group.created_by != request.user:
        return redirect('collaboration_group:collaboration_group_list')
    
    if request.method == 'POST':
        collaboration_group.delete()
        return redirect('collaboration_group:collaboration_group_list')
    return render(request, 'collaboration_group_confirm_delete.html', {'collaboration_group': collaboration_group})

@login_required
def manage_group(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)

    if group.created_by != request.user:
        return redirect('collaboration_group:collaboration_group_list')

    members = GroupMember.objects.filter(group=group)
    all_users = User.objects.exclude(id__in=members.values_list('user_id', flat=True))

    if request.method == 'POST':
        form = GroupMemberForm(request.POST, user_queryset=all_users)
        if form.is_valid():
            user_to_add = form.cleaned_data['user']
            if not GroupMember.objects.filter(group=group, user=user_to_add).exists():
                GroupMember.objects.create(group=group, user=user_to_add)
            return redirect('collaboration_group:manage_group', group_id=group.id)
    else:
        form = GroupMemberForm(user_queryset=all_users)

    return render(request, 'manage_group.html', {
        'group': group,
        'members': members,
        'form': form,
    })

@login_required
def remove_member(request, group_id, member_id):
    member = get_object_or_404(GroupMember, pk=member_id, group_id=group_id)
    group = member.group

    if group.created_by != request.user:
        return redirect('collaboration_group:collaboration_group_list')
    
    member.delete()
    return redirect('collaboration_group:manage_group', group_id=group_id)

@login_required
def check_members(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)
    members = GroupMember.objects.filter(group=group)

    return render(request, 'check_members.html', {
        'group': group,
        'members': members
    })
