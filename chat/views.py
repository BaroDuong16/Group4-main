from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Chat, User, GroupChat
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse

# @login_required
# def notifications_view(request):
#     # Fetch unread messages for the logged-in user
#     unread_messages = Chat.objects.filter(receiver=request.user, is_read=False)

#     notifications = [
#         {
#             'sender': message.sender.username,
#             'message': message.message,
#             'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#         }
#         for message in unread_messages
#     ]

#     return JsonResponse({
#         'unread_count': unread_messages.count(),
#         'notifications': notifications,  # Return notifications with sender info
#     })

def send_message_form(request):
    if request.method == "POST":
        recipient_username = request.POST.get('recipient')
        message_text = request.POST.get('message')
        sender_username = request.POST.get('sender')  # Assume sender is passed from the form
        recipient = get_object_or_404(User, username=recipient_username)
        sender = get_object_or_404(User, username=sender_username)
        if recipient and sender and message_text:
            Chat.objects.create(sender=sender, receiver=recipient, message=message_text)
            return redirect('chat:chat_view', username=recipient_username)  # Corrected redirect
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'chat/send_message_form.html', context)

def create_group_chat_view(request):
    if request.method == "POST":
        group_name = request.POST.get('group_name')  # Get group name from the form
        member_usernames = request.POST.getlist('members')  # List of selected usernames

        if group_name and member_usernames:
            # Create the group
            group = GroupChat.objects.create(name=group_name, created_by=request.user)

            # Add the selected members to the group
            for username in member_usernames:
                user = get_object_or_404(User, username=username)
                group.members.add(user)

            # Ensure the creator is also added to the group
            group.members.add(request.user)

            return redirect('chat:chat_view', group_id=group.id)

    # Get all users except the current user
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'chat/create_group_chat.html', {'users': users})

@login_required
def add_member_to_group_view(request, group_id):
    group = get_object_or_404(GroupChat, id=group_id)
    current_user = request.user

    # Ensure the current user is part of the group (either the creator or a member)
    if current_user not in group.members.all() and group.created_by != current_user:
        return redirect('some_error_page')  # Unauthorized access

    if request.method == "POST":
        member_usernames = request.POST.getlist('members')  # List of selected usernames

        # Add the selected members to the group
        for username in member_usernames:
            user = get_object_or_404(User, username=username)
            if user not in group.members.all():  # Avoid adding the same user again
                group.members.add(user)

        return redirect('chat:chat_view', group_id=group.id)

    # Get all users except those who are already in the group
    users = User.objects.exclude(id__in=group.members.all().values_list('id', flat=True))

    return render(request, 'chat/add_member_to_group.html', {'group': group, 'users': users})

@login_required
def remove_member_from_group_view(request, group_id):
    group = get_object_or_404(GroupChat, id=group_id)
    current_user = request.user

    # Ensure the current user is the creator of the group (only the creator can remove members)
    if group.created_by != current_user:
        return redirect('some_error_page')  # Unauthorized access

    if request.method == "POST":
        member_username = request.POST.get('member')  # Username of the member to remove
        member = get_object_or_404(User, username=member_username)

        if member != group.created_by:  # Prevent creator from removing themselves
            group.members.remove(member)

        return redirect('chat:chat_view', group_id=group.id)

    # Get all members of the group except the group creator
    members = group.members.exclude(id=group.created_by.id)

    return render(request, 'chat/remove_member_from_group.html', {'group': group, 'members': members})

@login_required
def edit_message_view(request, message_id):
    message = get_object_or_404(Chat, id=message_id)

    # Ensure the user is the sender of the message
    if message.sender != request.user:
        return redirect('some_error_page')  # Unauthorized access

    if request.method == "POST":
        new_message_text = request.POST.get('message', '').strip()
        if new_message_text:
            message.message = new_message_text
            message.edited_at = timezone.now()  # Set edited timestamp
            message.save()

            # Redirect back to the relevant group chat or direct chat
            if message.group:
                return redirect('chat:chat_view', group_id=message.group.id)
            else:
                return redirect('chat:chat_view', username=message.receiver.username)  # Changed here

    return render(request, 'chat/edit_message.html', {'message': message})

@login_required
def delete_message_view(request, message_id):
    message = get_object_or_404(Chat, id=message_id)

    # Ensure the user is the sender of the message
    if message.sender != request.user:
        return redirect('some_error_page')  # Unauthorized access

    if request.method == "POST":
        message.delete()
        # Redirect back to the relevant group chat or direct chat
        if message.group:
            return redirect('chat:chat_view', group_id=message.group.id)
        else:
            return redirect('chat:chat_view', username=message.receiver.username)  # Changed here

    return render(request, 'chat/delete_message.html', {'message': message})

def chat_view(request, username=None, group_id=None):
    current_user = request.user  # Get the current logged-in user
    
    # Get the search query from the request
    search_query = request.GET.get('q', '').strip()
    
    # Filter users based on the search query, excluding the current user
    if search_query:
        users = User.objects.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(first_name__icontains=search_query)| # Assuming full_name exists
            Q(last_name__icontains=search_query)
        ).exclude(id=current_user.id)
    else:
        # If no search query, list all users except the current user
        users = User.objects.exclude(id=current_user.id)

    # Filter group chats based on the search query
    if search_query:
        group_chats = GroupChat.objects.filter(
            Q(name__icontains=search_query) &
            (Q(created_by=current_user) | Q(members=current_user))
        ).distinct()
    else:
        # Get all group chats where the user is either the creator or a member
        group_chats = GroupChat.objects.filter(
            Q(created_by=current_user) | Q(members=current_user)
        ).distinct()

    if group_id:
        # Handle group chat
        group = get_object_or_404(GroupChat, id=group_id)

        # Ensure the current user is part of the group (either the creator or a member)
        if current_user not in group.members.all() and group.created_by != current_user:
            return redirect('some_error_page')  # Unauthorized access

        # Fetch group messages
        messages = Chat.objects.filter(group=group).order_by('timestamp')

        if request.method == "POST":
            message_text = request.POST.get('message', '').strip()
            if message_text:
                # Create a new message for the group
                Chat.objects.create(sender=current_user, group=group, message=message_text)
                return redirect('chat:chat_view', group_id=group.id)

        context = {
            'group': group,
            'messages': messages,
            'users': users,
            'group_chats': group_chats,
            'user': current_user  # Pass the current logged-in user
        }
    
    elif username:
        # Handle one-on-one chat
        other_user = get_object_or_404(User, username=username)  # The receiver (other participant in the chat)

        if current_user.username == username:
            # Prevent a user from chatting with themselves
            return redirect('some_error_page')  # Redirect to an error page or a relevant message

        # Filter messages between the logged-in user and the selected receiver
        messages = Chat.objects.filter(
            (Q(sender=current_user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=current_user))
        ).order_by('timestamp')

        if request.method == "POST":
            message_text = request.POST.get('message', '').strip()
            selected_receiver_username = request.POST.get('receiver', other_user.username)
            receiver = get_object_or_404(User, username=selected_receiver_username)
            
            if message_text and receiver:
                Chat.objects.create(sender=current_user, receiver=receiver, message=message_text)
                return redirect('chat:chat_view', username=other_user.username)

        context = {
            'other_user': other_user,
            'messages': messages,
            'users': users,
            'group_chats': group_chats,
            'user': current_user  # Pass the current logged-in user
        }
    else:
        # If no username or group_id is provided, just render the user list and group chats
        context = {
            'users': users,
            'group_chats': group_chats,
            'user': current_user
        }

    return render(request, 'chat/chat_view.html', context)
# @login_required
# def chat_view(request, username=None, group_id=None):
#     current_user = request.user  # Get the current logged-in user

#     # Get the search query from the request
#     search_query = request.GET.get('q', '').strip()
    
#     # Filter users based on the search query, excluding the current user
#     if search_query:
#         users = User.objects.filter(
#             Q(username__icontains=search_query) | 
#             Q(email__icontains=search_query) | 
#             Q(full_name__icontains=search_query)  # Assuming full_name exists
#         ).exclude(id=current_user.id)
#     else:
#         # If no search query, list all users except the current user
#         users = User.objects.exclude(id=current_user.id)

#     # Filter group chats based on the search query
#     if search_query:
#         group_chats = GroupChat.objects.filter(
#             Q(name__icontains=search_query) &
#             (Q(created_by=current_user) | Q(members=current_user))
#         ).distinct()
#     else:
#         # Get all group chats where the user is either the creator or a member
#         group_chats = GroupChat.objects.filter(
#             Q(created_by=current_user) | Q(members=current_user)
#         ).distinct()

#     if group_id:
#         # Handle group chat
#         group = get_object_or_404(GroupChat, id=group_id)

#         # Ensure the current user is part of the group (either the creator or a member)
#         if current_user not in group.members.all() and group.created_by != current_user:
#             return redirect('some_error_page')  # Unauthorized access

#         # Fetch group messages
#         messages = Chat.objects.filter(group=group).order_by('timestamp')

#         # Mark messages as read
#         Chat.objects.filter(group=group, receiver=current_user).update(is_read=True)

#         if request.method == "POST":
#             message_text = request.POST.get('message', '').strip()
#             if message_text:
#                 # Create a new message for the group
#                 Chat.objects.create(sender=current_user, group=group, message=message_text)
#                 return redirect('chat:chat_view', group_id=group.id)

#         context = {
#             'group': group,
#             'messages': messages,
#             'users': users,
#             'group_chats': group_chats,
#             'user': current_user  # Pass the current logged-in user
#         }
    
#     elif username:
#         # Handle one-on-one chat
#         other_user = get_object_or_404(User, username=username)  # The receiver (other participant in the chat)

#         if current_user.username == username:
#             # Prevent a user from chatting with themselves
#             return redirect('some_error_page')  # Redirect to an error page or a relevant message

#         # Filter messages between the logged-in user and the selected receiver
#         messages = Chat.objects.filter(
#             (Q(sender=current_user) & Q(receiver=other_user)) |
#             (Q(sender=other_user) & Q(receiver=current_user))
#         ).order_by('timestamp')

#         # Mark messages as read
#         Chat.objects.filter(
#             Q(sender=other_user, receiver=current_user) |
#             Q(sender=current_user, receiver=other_user)
#         ).update(is_read=True)

#         if request.method == "POST":
#             message_text = request.POST.get('message', '').strip()
#             selected_receiver_username = request.POST.get('receiver', other_user.username)
#             receiver = get_object_or_404(User, username=selected_receiver_username)
            
#             if message_text and receiver:
#                 Chat.objects.create(sender=current_user, receiver=receiver, message=message_text)
#                 return redirect('chat:chat_view', username=other_user.username)

#         context = {
#             'other_user': other_user,
#             'messages': messages,
#             'users': users,
#             'group_chats': group_chats,
#             'user': current_user  # Pass the current logged-in user
#         }
#     else:
#         # If no username or group_id is provided, just render the user list and group chats
#         context = {
#             'users': users,
#             'group_chats': group_chats,
#             'user': current_user
#         }

#     return render(request, 'chat/chat_view.html', context)