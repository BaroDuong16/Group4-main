from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model  # Import for custom user model
from .forms import CollaborationGroupForm, GroupMemberForm, GroupFeedbackForm, MemberFeedbackForm
from .models import CollaborationGroup, GroupMember, GroupFeedback, MemberFeedback
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

User = get_user_model()  # Reference the custom User model


@login_required
def my_groups_view(request):
    user_memberships = GroupMember.objects.filter(user=request.user)

    groups = CollaborationGroup.objects.filter(members__in=user_memberships)

    paginator = Paginator(groups, 10)  # Show 10 groups per page
    page_number = request.GET.get('page')  # Get the current page from the GET parameters
    page_obj = paginator.get_page(page_number)

    return render(request, 'my_groups.html', {'page_obj': page_obj})

@login_required
def collaboration_group_list(request):
    collaboration_groups = CollaborationGroup.objects.all()
    
    # Get all member IDs for the current user
    user_membership_ids = GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
    
    # Pagination logic
    paginator = Paginator(collaboration_groups, 10)  # Show 10 groups per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'collaboration_group_list.html', {
        'page_obj': page_obj,  # Pass paginated object to template
        'user_membership_ids': user_membership_ids
    })

@login_required
def join_group(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)
    
    # Check if the user is already a member
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        GroupMember.objects.create(group=group, user=request.user)

    return redirect('collaboration_group:collaboration_group_list')  # Redirect back to the group list

@login_required
def collaboration_group_add(request):
    if request.method == 'POST':
        form = CollaborationGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user  # Set the current user as the creator
            group.save()
            # Save ManyToMany field after the initial save
            form.save_m2m()  
            return redirect('collaboration_group:collaboration_group_list')
    else:
        form = CollaborationGroupForm()
    return render(request, 'collaboration_group_form.html', {'form': form})

@login_required
def collaboration_group_edit(request, pk):
    collaboration_group = get_object_or_404(CollaborationGroup, pk=pk)
    
    # Check if the logged-in user is the creator of the group
    if not (request.user == collaboration_group.created_by or request.user.is_superuser):
        return redirect('collaboration_group:collaboration_group_list')  # Redirect if user is not the creator
    
    if request.method == 'POST':
        form = CollaborationGroupForm(request.POST, instance=collaboration_group)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            form.save_m2m()  # Ensure ManyToMany relationships are saved
            return redirect('collaboration_group:collaboration_group_list')
    else:
        form = CollaborationGroupForm(instance=collaboration_group)
    return render(request, 'collaboration_group_form.html', {'form': form})

@login_required
def collaboration_group_delete(request, pk):
    collaboration_group = get_object_or_404(CollaborationGroup, pk=pk)
    
    # Only allow the creator or a superuser to delete the group
    if not (request.user == collaboration_group.created_by or request.user.is_superuser):
        return redirect('collaboration_group:collaboration_group_list')  # Redirect if user is not the creator
    
    if request.method == 'POST':
        collaboration_group.delete()
        return redirect('collaboration_group:collaboration_group_list')
    
    return render(request, 'collaboration_group_confirm_delete.html', {'collaboration_group': collaboration_group})


@login_required
def manage_group(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)

    # Check if the logged-in user is the creator of the group
    if not (request.user == group.created_by or request.user.is_superuser):
        return redirect('collaboration_group:collaboration_group_list') 

    members = GroupMember.objects.filter(group=group).order_by('joined_at')
    all_users = User.objects.exclude(id__in=members.values_list('user_id', flat=True))

    # Pagination
    paginator = Paginator(members, 10)  # Show 10 members per page
    page_number = request.GET.get('page')
    paginated_members = paginator.get_page(page_number)

    if request.method == 'POST':
        form = GroupMemberForm(request.POST, user_queryset=all_users)  # Pass user queryset
        if form.is_valid():
            user_to_add = form.cleaned_data['user']
            # Check if the user is already a member of the group
            if not GroupMember.objects.filter(group=group, user=user_to_add).exists():
                GroupMember.objects.create(group=group, user=user_to_add)  # Create new member
            return redirect('collaboration_group:manage_group', group_id=group.id)
    else:
        form = GroupMemberForm(user_queryset=all_users)  # Pass user queryset on GET

    return render(request, 'manage_group.html', {
        'group': group,
        'members': paginated_members,  # Use paginated members
        'form': form,  # Pass the form instance to the template
    })

@login_required
def check_members(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)
    members = GroupMember.objects.filter(group=group).order_by('joined_at')
    # Pagination
    paginator = Paginator(members, 10)  # Show 10 members per page
    page_number = request.GET.get('page')
    paginated_members = paginator.get_page(page_number)

    return render(request, 'check_members.html', {
        'group': group,
        'members': paginated_members  # Use paginated members
    })

@login_required
def remove_member(request, group_id, member_id):
    member = get_object_or_404(GroupMember, pk=member_id, group_id=group_id)
    group = member.group
    
    # Only allow the creator of the group to remove members
    if group.created_by != request.user:
        return redirect('collaboration_group:collaboration_group_list')  # Redirect if user is not the creator
    
    member.delete()
    return redirect('collaboration_group:manage_group', group_id=group_id)

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)

    # Check if the user is a member of the group
    membership = GroupMember.objects.filter(group=group, user=request.user).first()

    if membership:
        membership.delete()  # Remove the member from the group

    return redirect('collaboration_group:collaboration_group_list')  # Redirect back to the group list

@login_required
def user_list_view(request, group_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)

    # Get all users except those already in the group
    existing_members = GroupMember.objects.filter(group=group).values_list('user', flat=True)
    users = User.objects.exclude(id__in=existing_members)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )

    # Date range filter functionality
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    if start_date:
        from_date_parsed = parse_date(start_date)
        if from_date_parsed:  # Check if the parsed date is valid
            users = users.filter(date_joined__gte=from_date_parsed)

    if end_date:
        to_date_parsed = parse_date(end_date)
        if to_date_parsed:  # Check if the parsed date is valid
            # Add the entire day by setting the time to 23:59:59
            to_date_with_time = datetime.combine(to_date_parsed, datetime.max.time())
            users = users.filter(date_joined__lte=to_date_with_time)

    if request.method == 'POST':
        # Handle batch user addition
        selected_user_ids = request.POST.getlist('users')
        if selected_user_ids:
            for user_id in selected_user_ids:
                user = get_object_or_404(User, pk=user_id)
                GroupMember.objects.get_or_create(group=group, user=user)
            return redirect('collaboration_group:manage_group', group_id=group.id)
        else:
            return HttpResponseBadRequest('No users selected.')

    context = {
        'group': group,
        'users': users,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'user_list1.html', context)

@login_required
def add_member(request, group_id, user_id):
    group = get_object_or_404(CollaborationGroup, pk=group_id)
    user = get_object_or_404(User, pk=user_id)
    GroupMember.objects.get_or_create(group=group, user=user)
    return redirect('collaboration_group:manage_group', group_id=group.id)

@login_required
def group_feedback_view(request, group_id):
    group = get_object_or_404(CollaborationGroup, id=group_id)

    if request.method == 'POST':
        group_feedback_form = GroupFeedbackForm(request.POST)
        if group_feedback_form.is_valid():
            feedback = group_feedback_form.save(commit=False)
            feedback.group = group
            feedback.submitted_by = request.user
            feedback.save()
            return redirect('collaboration_group:collaboration_group_list')  # Redirect to group feedback list
    else:
        group_feedback_form = GroupFeedbackForm()

    context = {
        'group': group,
        'group_feedback_form': group_feedback_form,
    }
    return render(request, 'group_feedback.html', context)

@login_required
def member_feedback_view(request, group_id):
    group = get_object_or_404(CollaborationGroup, id=group_id)

    if request.method == 'POST':
        member_feedback_form = MemberFeedbackForm(request.POST, group=group)
        if member_feedback_form.is_valid():
            feedback = member_feedback_form.save(commit=False)
            feedback.group = group
            feedback.submitted_by = request.user
            feedback.member = member_feedback_form.cleaned_data['member']  # Assign selected member
            feedback.save()
            return redirect('collaboration_group:collaboration_group_list')  # Redirect to member feedback list
    else:
        member_feedback_form = MemberFeedbackForm(group=group)  # Filter members based on group

    context = {
        'group': group,
        'member_feedback_form': member_feedback_form,
    }
    return render(request, 'member_feedback.html', context)


@login_required
def view_feedbacks(request):
    groups = CollaborationGroup.objects.all()  # Fetch all groups for filtering
    selected_group = request.GET.get('group')  # Get the selected group from the query string

    # Filter feedbacks based on the selected group
    if selected_group:
        group_feedbacks = GroupFeedback.objects.filter(group_id=selected_group)
        member_feedbacks = MemberFeedback.objects.filter(group_id=selected_group)
    else:
        group_feedbacks = GroupFeedback.objects.all()
        member_feedbacks = MemberFeedback.objects.all()

    # Add pagination
    group_feedback_paginator = Paginator(group_feedbacks, 10)  # 10 items per page
    member_feedback_paginator = Paginator(member_feedbacks, 10)

    group_feedback_page = request.GET.get('group_feedback_page', 1)  # Current page for group feedbacks
    member_feedback_page = request.GET.get('member_feedback_page', 1)  # Current page for member feedbacks

    group_feedbacks = group_feedback_paginator.get_page(group_feedback_page)
    member_feedbacks = member_feedback_paginator.get_page(member_feedback_page)

    context = {
        'groups': groups,
        'selected_group': selected_group,
        'group_feedbacks': group_feedbacks,
        'member_feedbacks': member_feedbacks,
    }
    return render(request, 'view_feedbacks.html', context)

@login_required
def feedback_selection_view(request, group_id):
    group = get_object_or_404(CollaborationGroup, id=group_id)
    return render(request, 'feedback_selection.html', {'group': group})