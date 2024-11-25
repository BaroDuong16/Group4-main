from django.shortcuts import render, get_object_or_404, redirect
from .models import DiscussionThread, ThreadComments, ThreadReaction, CommentReaction,ReportThread
from .forms import ThreadForm, CommentForm,ThreadReportForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Case, When, IntegerField, F, Q, OuterRef, Subquery
from course.models import Course
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.contrib import messages
from module_group.models import ModuleGroup
from django.http import HttpResponseBadRequest
from django.db.models import F

@login_required
def thread_list(request, course_id=None):
    q = request.GET.get('q', '')
    selected_course = Course.objects.filter(id=course_id).first() if course_id else None
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
    comments_subquery = ThreadComments.objects.filter(
    thread_id=OuterRef('pk')
    ).values('thread_id').annotate(count=Count('comment_id')).values('count')

    # Apply annotations for likes, loves, comments, and interactions
    threads = threads.annotate(
    total_likes  = Count('reactions', filter=Q(reactions__reaction_type='like')),
    total_loves  = Count('reactions', filter=Q(reactions__reaction_type='love')),
    total_haha   = Count('reactions', filter=Q(reactions__reaction_type='haha')),
    total_wow    = Count('reactions', filter=Q(reactions__reaction_type='wow')),
    total_sad    = Count('reactions', filter=Q(reactions__reaction_type='sad')),
    total_angry  = Count('reactions', filter=Q(reactions__reaction_type='angry')),
    total_comments=Coalesce(Subquery(comments_subquery, output_field=IntegerField()), 0)
)

    # Then calculate total_reactions and total_interactions
    threads = threads.annotate(
        total_reactions = F('total_likes') + F('total_loves') + F('total_haha') + F('total_wow') + F('total_sad') + F('total_angry'),
        total_interactions = F('total_comments') + F('total_reactions'),
    ).order_by('-total_interactions', '-created')
    
    threads = threads.annotate(
        total_interactions = F('total_comments') + F('total_reactions'),
    ).order_by('-total_interactions', '-created')

    user_reactions = {reaction.thread_id: reaction.reaction_type
                    for reaction in ThreadReaction.objects.filter(user=request.user, thread__in=threads)}
    recent_activities = threads.order_by('-created')
    module_groups = ModuleGroup.objects.all()
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
    
    user_reactions = ThreadReaction.objects.filter(user=request.user, thread__in=threads).values('thread_id', 'reaction_type')
    
    

    # Context for rendering templates
    context = {
        'threads': page_obj,  # Use the paginated threads
        'courses': courses,
        'query': q,
        'recent_activities': recent_activities,
        'featured_threads': featured_threads,
        'module_groups' : module_groups,
        'selected_course':selected_course,
        

    }
    context1 = {
        'threads': page_obj1,  # Use the paginated threads
        'courses': courses,
        'query': q,
        'recent_activities': recent_activities,
        'featured_threads': featured_threads,
        'module_groups' : module_groups,
        'user_reactions':user_reactions,
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
    likes_count = thread.likes_count
    loves_count = thread.loves_count
    haha_count = thread.haha_count
    wow_count = thread.wow_count
    sad_count = thread.sad_count
    angry_count = thread.angry_count
    module_groups = ModuleGroup.objects.all()
    # Prepare a list to hold comments with their reaction counts
    comments_with_reactions = []
    for comment in thread.comments.all():
        # Get likes and loves counts for each comment
        comment_likes_count = CommentReaction.objects.filter(comment=comment, reaction_type='like').count()
        comment_loves_count = CommentReaction.objects.filter(comment=comment, reaction_type='love').count()
        comment_haha_count = CommentReaction.objects.filter(comment=comment, reaction_type='haha').count()
        comment_wow_count = CommentReaction.objects.filter(comment=comment, reaction_type='wow').count()
        comment_sad_count = CommentReaction.objects.filter(comment=comment, reaction_type='sad').count()
        comment_angry_count = CommentReaction.objects.filter(comment=comment, reaction_type='angry').count()
        # Append the comment and its reaction counts to the list
        comments_with_reactions.append({
            'comment': comment,
            'comment_likes_count': comment_likes_count,
            'comment_loves_count': comment_loves_count,
            'comment_haha_count':comment_haha_count,
            'comment_wow_count':comment_wow_count,
            'comment_sad_count':comment_sad_count,
            'comment_angry_count':comment_angry_count,
        })
    
    # Prepare context data for the template
    context = {
        'thread': thread,
        'likes_count': likes_count,
        'loves_count': loves_count,
        'haha_count':haha_count,
        'wow_count':wow_count,
        'sad_count':sad_count,
        'angry_count':angry_count,
        'comments_with_reactions': comments_with_reactions,
        'module_groups': module_groups,
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

    if not created and reaction.reaction_type != reaction_type:
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
        if not created :
            reaction.reaction_type = reaction_type
            reaction.save()

        # Calculate new counts
        likes_count = thread.likes_count  # This will dynamically calculate likes
        loves_count = thread.loves_count  
        haha_count = thread.haha_count
        wow_count = thread.wow_count
        sad_count = thread.sad_count
        angry_count = thread.angry_count
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'likes_count': likes_count,
                'loves_count': loves_count,
                'haha_count':haha_count,
                'wow_count':wow_count,
                'sad_count':sad_count,
                'angry_count':angry_count,
                'message': "Reaction updated successfully."
            })

        # Determine the referrer to decide where to redirect
        referrer = request.META.get('HTTP_REFERER', '')
        if 'thread/detail' in referrer:
            return redirect('thread:thread_detail', pk=thread.pk)
        else:
            return redirect('thread:thread_list')
        
        
    return HttpResponseBadRequest("Invalid request method.")


# @login_required
# def react_to_thread(request, thread_id):
#     if request.method == 'POST':
#         # Retrieve the thread with annotated reaction counts for each type
#         thread = get_object_or_404(DiscussionThread, id=thread_id)

#         # Get the reaction type from the request
#         reaction_type = request.POST.get('reaction_type')

#         # Validate the reaction type
#         if reaction_type not in dict(ThreadReaction.REACTION_CHOICES).keys():
#             return HttpResponseBadRequest("Invalid reaction type.")

#         # Get or create a reaction
#         reaction, created = ThreadReaction.objects.get_or_create(
#             user=request.user,
#             thread=thread,
#             reaction_type= reaction_type
#         )

#         # Update reaction type if it already exists
#         if not created:
#             # If the reaction already exists, update the reaction type
#             if reaction.reaction_type == reaction_type:
#                 # Remove the reaction if the same type is clicked again
#                 reaction.delete()
#                 message = "Reaction removed."
#             else:
#                 # Update the reaction type
#                 reaction.reaction_type = reaction_type
#                 reaction.save()
#                 message = "Reaction updated successfully."
#         else:
#             message = "Reaction added successfully."
        

#         # Calculate updated counts for each reaction type
#         reaction_counts = thread.reactions.values('reaction_type').annotate(count=models.Count('id'))
#         total_reactions = {item['reaction_type']: item['count'] for item in reaction_counts}

#         # Return JSON response for AJAX requests
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'total_reactions': total_reactions,
#                 'message': message,
#             })

#         # Redirect based on the referrer URL
#         referrer = request.META.get('HTTP_REFERER', '')
#         if 'thread/detail' in referrer:
#             return redirect('thread:thread_detail', pk=thread.pk)
#         else:
#             return redirect('thread:thread_list')

#     return HttpResponseBadRequest("Invalid request method.")









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


def report_thread(request, thread_id):
    thread = get_object_or_404(DiscussionThread, id=thread_id)
    
    if request.method == 'POST':
        form = ThreadReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.thread = thread
            report.reported_by = request.user  # Ensure this field exists in your report model
            report.save()
            messages.success(request, 'Your report has been submitted.')
            return redirect('thread:thread_list')  # Redirect after successful submission
    else:
        # For GET request, instantiate the form
        form = ThreadReportForm()
    
    # Render the template with the thread and form
    return render(request, 'thread/report_thread.html', {'thread': thread, 'form': form})


def view_reports(request):
    # Get the search query from the request
    query = request.GET.get('q', '')

    # Filter reports based on the search query if provided
    if query:
        reports = ReportThread.objects.filter(
            Q(thread__thread_title__icontains=query) |  # Adjust based on your thread model
            Q(reported_by__username__icontains=query) |  # Assuming 'reported_by' is a user field
            Q(reason__icontains=query)  # Assuming there is a reason field
        )
    else:
        reports = ReportThread.objects.all()
    
    paginator = Paginator(reports, 10)  # 10 threads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    module_groups = ModuleGroup.objects.all()
    return render(request, 'thread/view_reports.html', {'reports': page_obj, 'query': query,'module_groups': module_groups})


def recent_activity(request):
    module_groups = ModuleGroup.objects.all()
    query = request.GET.get('q', '')
    # Filter reports based on the search query if provided
    if query:
        recent_activities = DiscussionThread.objects.filter(
            Q(thread_title__icontains=query) |  # Adjust based on your thread model
            Q(created_by__username__icontains=query) |# Assuming 'reported_by' is a user field
            Q(course__course_name__icontains = query)
        )
    else:
        recent_activities = DiscussionThread.objects.all()
    
    
    
    paginator = Paginator(recent_activities,15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'recent_activities':page_obj,
        'module_groups':module_groups,
        'query':query
    }
    return render(request,'thread/recent_activity.html',context)


@login_required
def user_feed(request):
    # Fetch all threads created by the logged-in user
    user_threads = DiscussionThread.objects.filter(created_by=request.user).order_by('-created')

    # Set up pagination
    paginator = Paginator(user_threads, 5)  # Show 10 threads per page
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)

    return render(request, 'thread/user_feed.html', {'page_obj': page_obj})