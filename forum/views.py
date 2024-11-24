from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ForumQuestion, ForumComment, Reply, Report
from .forms import ForumQuestionForm, ForumCommentForm, ReplyForm, ReportForm
from course.models import Course
from django.core.paginator import Paginator
from module_group.models import ModuleGroup, Module
from user.models import User
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def question_list(request):
    selected_course_id = request.GET.get('course_id')  # Change 'id' to 'course_id'
    selected_creator_id = request.GET.get('creator_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Get all courses for the dropdown
    courses = Course.objects.all()
    users = User.objects.all()

    # Filter questions based on selected course, or show all questions
    questions = ForumQuestion.objects.all()

    if selected_course_id:
        questions = questions.filter(course_id=selected_course_id)
    if selected_creator_id:
        questions = questions.filter(user_id=selected_creator_id)
    if start_date:
        questions = questions.filter(created_at__gte=start_date)
    if end_date:
        questions = questions.filter(created_at__lte=end_date)

    questions = questions.order_by('-created_at')

    # Pagination logic: paginate questions, 10 per page
    paginator = Paginator(questions, 10)  # Show 10 questions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    module_groups = ModuleGroup.objects.all()
    module = Module.objects.all()

    return render(request, 'forum_question_list.html', {
        'page_obj': page_obj,
        'courses': courses,
        'users': users,
        'selected_course_id': int(selected_course_id) if selected_course_id else None,
        'selected_creator_id': int(selected_creator_id) if selected_creator_id else None,
        'start_date': start_date,
        'end_date': end_date,
        'module_groups': module_groups,
        'module': module,
    })

@login_required
def question_detail(request, pk):
    question = get_object_or_404(ForumQuestion, pk=pk)

    if request.method == 'POST':
        comment_form = ForumCommentForm(request.POST, request.FILES)
        reply_form = ReplyForm(request.POST, request.FILES)

        if 'submit_comment' in request.POST and comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.question = question
            comment.save()
            return redirect('forum:question_detail', pk=pk)

        elif 'submit_reply' in request.POST and reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.user = request.user

            # Check if replying to a comment or another reply
            if request.POST.get('comment_id'):
                reply.comment = ForumComment.objects.get(pk=request.POST.get('comment_id'))
            elif request.POST.get('reply_id'):
                reply.parent_reply = Reply.objects.get(pk=request.POST.get('reply_id'))

            reply.save()
            return redirect('forum:question_detail', pk=pk)

    comment_form = ForumCommentForm()
    reply_form = ReplyForm()

    return render(request, 'forum_question_detail.html', {
        'question': question,
        'comments': question.comments.all(),
        'comment_form': comment_form,
        'reply_form': reply_form,
    })

@login_required
def create_question(request):
    courses = Course.objects.all()  # Fetch all courses
    if request.method == 'POST':
        form = ForumQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user  # Set the user field
            question.save()
            return redirect('forum:question_list')
    else:
        form = ForumQuestionForm()
    return render(request, 'forum_create_question.html', {'form': form, 'courses': courses})

@login_required
def edit_question(request, pk):
    question = get_object_or_404(ForumQuestion, pk=pk)
    courses = Course.objects.all()  # Fetch all courses
    if request.method == 'POST':
        form = ForumQuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            if 'image-clear' in request.POST:
                question.image.delete()
            question = form.save(commit=False)
            width = form.cleaned_data.get('width')
            height = form.cleaned_data.get('height')
            if width and height and question.image:
                question.image = resize_image(question.image, width, height)
            question.save()
            return redirect('forum:question_detail', pk=pk)
    else:
        form = ForumQuestionForm(instance=question)
    return render(request, 'forum_edit_question.html', {'form': form, 'courses': courses})

@login_required
def delete_question(request, pk):
    question = get_object_or_404(ForumQuestion, pk=pk)
    if request.method == 'POST':
        question.delete()
        return redirect('forum:question_list')
    return render(request, 'forum_confirm_delete.html', {'object': question})

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(ForumComment, pk=pk)
    if request.method == 'POST':
        form = ForumCommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            if 'image-clear' in request.POST:
                comment.image.delete()
            form.save()
            return redirect('forum:question_detail', pk=comment.question.pk)
    else:
        form = ForumCommentForm(instance=comment)
    return render(request, 'forum_edit_comment.html', {'form': form})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(ForumComment, pk=pk)
    if request.method == 'POST':
        question_pk = comment.question.pk
        comment.delete()
        return redirect('forum:question_detail', pk=question_pk)
    return render(request, 'forum_confirm_delete.html', {'object': comment})

@login_required
def edit_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.method == 'POST':
        form = ReplyForm(request.POST, request.FILES, instance=reply)
        if form.is_valid():
            if 'image-clear' in request.POST:
                reply.image.delete()
            form.save()
            return redirect('forum:question_detail', pk=reply.comment.question.pk if reply.comment else reply.parent_reply.comment.question.pk)
    else:
        form = ReplyForm(instance=reply)
    return render(request, 'forum_edit_reply.html', {'form': form})

@login_required
def delete_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.method == 'POST':
        question_pk = reply.comment.question.pk if reply.comment else reply.parent_reply.comment.question.pk
        reply.delete()
        return redirect('forum:question_detail', pk=question_pk)
    return render(request, 'forum_confirm_delete.html', {'object': reply})

@login_required
def like_question(request, pk):
    question = get_object_or_404(ForumQuestion, pk=pk)
    if request.user in question.likes.all():
        question.likes.remove(request.user)
    else:
        question.likes.add(request.user)
        question.dislikes.remove(request.user)
    return redirect('forum:question_detail', pk=pk)

@login_required
def dislike_question(request, pk):
    question = get_object_or_404(ForumQuestion, pk=pk)
    if request.user in question.dislikes.all():
        question.dislikes.remove(request.user)
    else:
        question.dislikes.add(request.user)
        question.likes.remove(request.user)
    return redirect('forum:question_detail', pk=pk)

@login_required
def like_comment(request, pk):
    comment = get_object_or_404(ForumComment, pk=pk)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
    return redirect('forum:question_detail', pk=comment.question.pk)

@login_required
def dislike_comment(request, pk):
    comment = get_object_or_404(ForumComment, pk=pk)
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)
    return redirect('forum:question_detail', pk=comment.question.pk)

@login_required
def like_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
    else:
        reply.likes.add(request.user)
        reply.dislikes.remove(request.user)
    return redirect('forum:question_detail', pk=reply.comment.question.pk if reply.comment else reply.parent_reply.comment.question.pk)

@login_required
def dislike_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.user in reply.dislikes.all():
        reply.dislikes.remove(request.user)
    else:
        reply.dislikes.add(request.user)

@login_required
def report_content(request, report_type, report_id):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.report_type = report_type
            report.report_id = report_id
            report.save()
            return redirect('forum:question_list')
    else:
        form = ReportForm()
    return render(request, 'forum_report_content.html', {'form': form, 'report_type': report_type, 'report_id': report_id})


@login_required
def report_list(request):
    if not request.user.is_superuser:
        return redirect('main:home')
    reports = Report.objects.all().order_by('-created_at')
    reported_contents = [
        (report, get_reported_content(report.report_type, report.report_id))
        for report in reports
    ]
    return render(request, 'forum_report_list.html', {'reported_contents': reported_contents})


def get_reported_content(report_type, report_id):
    if report_type == 'question':
        return get_object_or_404(ForumQuestion, pk=report_id)
    elif report_type == 'comment':
        return get_object_or_404(ForumComment, pk=report_id)
    elif report_type == 'reply':
        return get_object_or_404(Reply, pk=report_id)
    return None

def resize_image(image, width, height):
    img = Image.open(image)
    img = img.resize((width, height), Image.ANTIALIAS)
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue())

