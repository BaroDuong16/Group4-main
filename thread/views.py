from django.shortcuts import render, get_object_or_404, redirect
from .models import DiscussionThread, ThreadComments, ThreadReaction, CommentReaction
from .forms import ThreadForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Case, When, IntegerField
from course.models import Course
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count

from django.http import HttpResponseBadRequest

@login_required
def thread_list(request, course_id=None):
    q = request.GET.get('q', '')

    if course_id:
        threads = DiscussionThread.objects.filter(
            Q(thread_title__icontains=q) |
            Q(thread_content__icontains=q) |
            Q(created_by__username__icontains=q),
            course_id=course_id
        )
    else:
        threads = DiscussionThread.objects.filter(
            Q(thread_title__icontains=q) |
            Q(thread_content__icontains=q) |
            Q(created_by__username__icontains=q)
        )
    
    # Apply annotations for likes, loves, comments, and interactions
    threads = threads.annotate(
        total_likes=Count(Case(When(reactions__reaction_type='like', then=1), output_field=IntegerField())),
        total_loves=Count(Case(When(reactions__reaction_type='love', then=1), output_field=IntegerField())),
        total_comments=Count('comments'),
        total_interactions=Count('reactions') + Count('comments')
    ).order_by('-total_interactions', '-created')
    
    recent_activities = threads.order_by('-created')
    # Featured threads (do not slice the main queryset)
    featured_threads = threads[:3]
    
    # For superuser
    paginator = Paginator(threads, 5)  # 5 threads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Fetch all courses
    courses = Course.objects.all()
    
    
    threads = threads[3:]
    # Apply pagination on the remaining threads
    paginator1 = Paginator(threads, 5)  # 5 threads per page
    page_number1 = request.GET.get('page')
    page_obj1 = paginator1.get_page(page_number1)
    
    
    

    # Context for rendering templates
    context = {
        'threads': page_obj,  # Use the paginated threads
        'courses': courses,
        'query': q,
        'recent_activities': recent_activities,
        'featured_threads': featured_threads,
    }
    context1 = {
        'threads': page_obj1,  # Use the paginated threads
        'courses': courses,
        'query': q,
        'recent_activities': recent_activities,
        'featured_threads': featured_threads,
    }

    # Render different templates based on user role
    if request.user.is_superuser:
        return render(request, 'thread/thread_list.html', context)
    
    return render(request, 'thread/thread_list_stu.html', context1)


# Create Thread
@login_required
def createThread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST,request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.created_by = request.user
            thread.save()
            return redirect('thread:thread_list')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = ThreadForm()

    return render(request, 'thread/thread_form.html', {'form': form})


# Update Thread
@login_required
def updateThread(request, pk):
    thread = get_object_or_404(DiscussionThread, pk=pk)

    if request.user != thread.created_by and not request.user.is_superuser:
        return redirect('thread:thread_list')

    if request.method == 'POST':
        form = ThreadForm(request.POST,request.FILES, instance=thread)
        if form.is_valid():
            form.save()
            return redirect('thread:thread_list')
    else:
        form = ThreadForm(instance=thread)

    return render(request, 'thread/thread_form.html', {'form': form})


# Delete Thread
@login_required
def deleteThread(request, pk):
    thread = get_object_or_404(DiscussionThread, pk=pk)

    if request.user != thread.created_by and not request.user.is_superuser:
        return redirect('thread:thread_list')

    if request.method == 'POST':
        thread.delete()
        return redirect('thread:thread_list')

    return render(request, 'thread/thread_confirm_delete.html', {'thread': thread})



def thread_detail(request, pk):
    # Get the thread object or return 404 if it doesn't exist
    thread = get_object_or_404(DiscussionThread, pk=pk)
    
    # Get the likes and loves counts for the thread
    likes_count = ThreadReaction.objects.filter(thread=thread, reaction_type='like').count()
    loves_count = ThreadReaction.objects.filter(thread=thread, reaction_type='love').count()
    
    # Prepare a list to hold comments with their reaction counts
    comments_with_reactions = []
    for comment in thread.comments.all():
        # Get likes and loves counts for each comment
        comment_likes_count = CommentReaction.objects.filter(comment=comment, reaction_type='like').count()
        comment_loves_count = CommentReaction.objects.filter(comment=comment, reaction_type='love').count()
        
        # Append the comment and its reaction counts to the list
        comments_with_reactions.append({
            'comment': comment,
            'likes_count': comment_likes_count,
            'loves_count': comment_loves_count,
        })
    
    # Prepare context data for the template
    context = {
        'thread': thread,
        'likes_count': likes_count,
        'loves_count': loves_count,
        'comments_with_reactions': comments_with_reactions,
    }
    
    # Render the template with the context data
    return render(request, 'thread/thread_detail.html', context)


# Add Comment
@login_required
def add_comment(request, pk):
    thread = get_object_or_404(DiscussionThread, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST,request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thread = thread
            comment.user = request.user
            comment.save()
            return redirect('thread:thread_detail', pk=thread.pk)
    else:
        form = CommentForm()

    comments = thread.comments.all()
    return render(request, 'thread/thread_detail.html', {'thread': thread, 'comments': comments, 'form': form})


# Update Comment
@login_required
def update_comment(request, pk, comment_id):
    comment = get_object_or_404(ThreadComments, pk=comment_id)

    if request.user != comment.user and not request.user.is_superuser:
        return redirect('thread:thread_detail', pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST,request.FILES, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('thread:thread_detail', pk=pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'thread/comment_form.html', {'form': form, 'comment': comment})


# Delete Comment
@login_required
def delete_comment(request, pk, comment_id):
    thread = get_object_or_404(DiscussionThread, pk=pk)
    comment = get_object_or_404(ThreadComments, pk=comment_id, thread=thread)

    if request.user != comment.user and not request.user.is_superuser:
        return redirect('thread:thread_detail', pk=thread.pk)

    if request.method == 'POST':
        comment.delete()
        return redirect('thread:thread_detail', pk=thread.pk)

    return render(request, 'thread/comment_confirm_delete.html', {'comment': comment})


# Add Reaction to Thread
@login_required
def add_reaction_to_thread(request, pk, reaction_type):
    thread = get_object_or_404(DiscussionThread, pk=pk)

    reaction, created = ThreadReaction.objects.get_or_create(
        user=request.user,
        thread=thread,
        defaults={'reaction_type': reaction_type}
    )

    if not created:
        reaction.reaction_type = reaction_type
        reaction.save()

    return redirect('thread:thread_detail', pk=pk)


# Add Reaction to Comment
@login_required
def add_reaction_to_comment(request, comment_id, reaction_type):
    comment = get_object_or_404(ThreadComments, pk=comment_id)

    reaction, created = CommentReaction.objects.get_or_create(
        user=request.user,
        comment=comment,
        defaults={'reaction_type': reaction_type}
    )

    if not created:
        reaction.reaction_type = reaction_type
        reaction.save()

    return redirect('thread:thread_detail', pk=comment.thread.pk)


def moderation_warning(request):
    return render(request, 'thread/moderation_warning.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from .models import DiscussionThread, ThreadReaction

@login_required
def react_to_thread(request, thread_id):
    if request.method == 'POST':
        thread = get_object_or_404(DiscussionThread, id=thread_id)
        reaction_type = request.POST.get('reaction_type')

        if reaction_type not in dict(ThreadReaction.REACTION_CHOICES).keys():
            return HttpResponseBadRequest("Invalid reaction type.")

        # Check if the user has already reacted to this thread
        reaction, created = ThreadReaction.objects.get_or_create(
            user=request.user,
            thread=thread,
            defaults={'reaction_type': reaction_type}
        )

        # If the reaction already exists but is different, update it
        if not created and reaction.reaction_type != reaction_type:
            reaction.reaction_type = reaction_type
            reaction.save()

        # Calculate new counts
        likes_count = ThreadReaction.objects.filter(thread=thread, reaction_type='like').count()
        loves_count = ThreadReaction.objects.filter(thread=thread, reaction_type='love').count()

        # Determine the referrer to decide where to redirect
        referrer = request.META.get('HTTP_REFERER', '')
        if 'thread/detail' in referrer:
            return redirect('thread:thread_detail', pk=thread.pk)
        else:
            return redirect('thread:thread_list')
        
    return HttpResponseBadRequest("Invalid request method.")

@require_POST
def react_to_comment(request, comment_id):
    reaction_type = request.POST.get('reaction_type')
    comment = get_object_or_404(ThreadComments, pk=comment_id)

    # Check if the user has already reacted
    existing_reaction = CommentReaction.objects.filter(user=request.user, comment=comment)

    if existing_reaction.exists():
        # Update existing reaction
        existing_reaction.update(reaction_type=reaction_type)
    else:
        # Create new reaction
        CommentReaction.objects.create(user=request.user, comment=comment, reaction_type=reaction_type)

    # Calculate new counts
    likes_count = CommentReaction.objects.filter(comment=comment, reaction_type='like').count()
    loves_count = CommentReaction.objects.filter(comment=comment, reaction_type='love').count()

    # Redirect back to the thread detail page
    return redirect('thread:thread_detail', pk=comment.thread.pk)


def report_dashboard(request):
    # Thread stats
    total_threads = DiscussionThread.objects.count()
    total_comments = ThreadComments.objects.count()

    # Reactions breakdown for threads
    thread_reactions = ThreadReaction.objects.values('reaction_type').annotate(count=Count('reaction_type'))

    # Reactions breakdown for comments
    comment_reactions = CommentReaction.objects.values('reaction_type').annotate(count=Count('reaction_type'))

    # Top threads with the most comments
    top_threads = DiscussionThread.objects.annotate(comment_count=Count('comments')).order_by('-comment_count')[:5]

    context = {
        'total_threads': total_threads,
        'total_comments': total_comments,
        'thread_reactions': thread_reactions,
        'comment_reactions': comment_reactions,
        'top_threads': top_threads,
    }

    return render(request, 'thread/report_dashboard.html', context)

