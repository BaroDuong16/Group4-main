from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from quiz.models import Quiz, Question, AnswerOption, StudentQuizAttempt, StudentAnswer
from course.models import Course
from subject.models import Subject
from django.db import transaction
from django.utils import timezone
from module_group.models import ModuleGroup
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from quiz.views import _get_quiz_result_context

# Create your views here.
@login_required
def quiz_list(request):
    module_groups = ModuleGroup.objects.all()
    courses = Course.objects.all()
    quizzes = Quiz.objects.select_related('course').annotate(question_count=Count('questions')).all().order_by('-created_at')
    selected_course = request.GET.get('course')
    
    if selected_course:
        quizzes = quizzes.filter(course__id=selected_course)  # Correct filter

    quiz_data = []  # Danh sách để lưu thông tin quiz và kết quả

    for quiz in quizzes:
        last_attempt = quiz.studentquizattempt_set.filter(user=request.user).last()
        marks = "0/0"
        grade = 0

        if last_attempt:
            total_questions = quiz.questions.count()
            correct_answers = 0
            for question in quiz.questions.all():
                try:
                    student_answer = StudentAnswer.objects.get(attempt=last_attempt, question=question)
                    if student_answer.selected_option and student_answer.selected_option.is_correct:
                        correct_answers += 1
                except StudentAnswer.DoesNotExist:
                    pass # Trường hợp học sinh chưa trả lời câu hỏi này

            marks = f"{correct_answers}/{total_questions}"
            if total_questions > 0:
                grade = (10 / total_questions) * correct_answers

        quiz_data.append({
            'quiz': quiz,
            'marks': marks,
            'grade': round(grade, 2),  # Làm tròn đến 2 chữ số thập phân
            'last_attempt': last_attempt
        })


    context = {
        'module_groups': module_groups,
        'quiz_data': quiz_data,  # Truyền quiz_data vào context
        'courses': courses,
        'selected_course': selected_course,
    }
    return render(request, 'quiz_list_student.html', context)
    


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz_detail_student.html', {'quiz': quiz, 'questions': questions})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()  # Lấy tất cả các câu hỏi trong quiz
    total_marks = quiz.total_marks  # Lấy tổng số điểm được định nghĩa cho quiz
    total_questions = questions.count()

    if request.method == 'POST':
        # Khi người dùng gửi form (submit quiz)
        with transaction.atomic():
            # Tạo một lần thử quiz mới cho học sinh
            attempt = StudentQuizAttempt.objects.create(user=request.user, quiz=quiz, score=0.0)

            correct_answers = 0
            for question in questions:
                selected_option_id = request.POST.get(f'question_{question.id}')  # Lấy lựa chọn được chọn cho câu hỏi
                text_response = request.POST.get(f'text_response_{question.id}')  # Thay đổi tên ở đây
                # Nếu câu hỏi là một câu hỏi dạng text, không cần truy xuất selected_option
                selected_option = None
                if selected_option_id and selected_option_id.isdigit():
                    selected_option = AnswerOption.objects.get(id=int(selected_option_id))
                # Lưu câu trả lời của học sinh
                StudentAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected_option,
                    text_response=text_response 
                )

                # Kiểm tra nếu lựa chọn đúng, cộng điểm
                if selected_option and selected_option.is_correct:
                    correct_answers += 1
            
            final_score = (total_marks / total_questions) * correct_answers

            # Cập nhật điểm tổng của lần thử
            attempt.score = final_score
            attempt.save()

            return redirect('std_quiz:quiz_result', quiz_id=quiz.id, attempt_id=attempt.id)  # Chuyển tới trang kết quả sau khi nộp bài

    # Render trang quiz với câu hỏi và lựa chọn
    return render(request, 'take_quiz_student.html', {'quiz': quiz, 'questions': questions})

@login_required
def quiz_result(request, quiz_id, attempt_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(StudentQuizAttempt, id=attempt_id, user=request.user)
    
    # Fetch the student answers related to this attempt
    student_answers = StudentAnswer.objects.filter(attempt=attempt)
    
    # Get all questions and their corresponding answer options for display
    questions_with_options = []
    for answer in student_answers:
        question = answer.question
        options = AnswerOption.objects.filter(question=question)
        questions_with_options.append({
            'question': question,
            'options': options,
            'selected_option': answer.selected_option
        })

    return render(request, 'quiz_student_result.html', {
        'quiz': quiz,
        'attempt': attempt,
        'questions_with_options': questions_with_options,
    })


@login_required
def take_quiz_invited(request, quiz_id):  # View mới cho người được mời
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    total_marks = quiz.total_marks
    total_questions = questions.count()

    if request.method == 'POST':
        # Khi người dùng gửi form (submit quiz)
        with transaction.atomic():
            # Tạo một lần thử quiz mới cho học sinh
            attempt = StudentQuizAttempt.objects.create(user=request.user, quiz=quiz, score=0.0)

            correct_answers = 0
            for question in questions:
                selected_option_id = request.POST.get(f'question_{question.id}')  # Lấy lựa chọn được chọn cho câu hỏi
                text_response = request.POST.get(f'text_response_{question.id}')  # Thay đổi tên ở đây
                # Nếu câu hỏi là một câu hỏi dạng text, không cần truy xuất selected_option
                selected_option = None
                if selected_option_id and selected_option_id.isdigit():
                    selected_option = AnswerOption.objects.get(id=int(selected_option_id))
                # Lưu câu trả lời của học sinh
                StudentAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected_option,
                    text_response=text_response 
                )

                # Kiểm tra nếu lựa chọn đúng, cộng điểm
                if selected_option and selected_option.is_correct:
                    correct_answers += 1
            
            final_score = (total_marks / total_questions) * correct_answers

            # Cập nhật điểm tổng của lần thử
            attempt.score = final_score
            attempt.save()

            return redirect('std_quiz:quiz_result_invited', quiz_id=quiz.id, attempt_id=attempt.id)  # Chuyển tới trang kết quả sau khi nộp bài

    return render(request, 'take_quiz_invited.html', {'quiz': quiz, 'questions': questions}) # Template mới


@login_required
def quiz_result_invited(request, quiz_id, attempt_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(StudentQuizAttempt, id=attempt_id, user=request.user)
    context = _get_quiz_result_context(quiz, attempt) # Sử dụng hàm chung
    return render(request, 'quiz_result_invited.html', context)

@login_required
def quiz_list_invite(request):
    courses = Course.objects.all()
    quizzes = Quiz.objects.select_related('course').annotate(question_count=Count('questions')).all().order_by('-created_at')
    selected_course = request.GET.get('course')
    
    if selected_course:
        quizzes = quizzes.filter(course__id=selected_course)  # Correct filter

    quiz_data = []  # Danh sách để lưu thông tin quiz và kết quả

    for quiz in quizzes:
        last_attempt = quiz.studentquizattempt_set.filter(user=request.user).last()
        marks = "0/0"
        grade = 0

        if last_attempt:
            total_questions = quiz.questions.count()
            correct_answers = 0
            for question in quiz.questions.all():
                try:
                    student_answer = StudentAnswer.objects.get(attempt=last_attempt, question=question)
                    if student_answer.selected_option and student_answer.selected_option.is_correct:
                        correct_answers += 1
                except StudentAnswer.DoesNotExist:
                    pass # Trường hợp học sinh chưa trả lời câu hỏi này

            marks = f"{correct_answers}/{total_questions}"
            if total_questions > 0:
                grade = (10 / total_questions) * correct_answers

        quiz_data.append({
            'quiz': quiz,
            'marks': marks,
            'grade': round(grade, 2)  # Làm tròn đến 2 chữ số thập phân
        })


    context = {
        'quiz_data': quiz_data,  # Truyền quiz_data vào context
        'courses': courses,
        'selected_course': selected_course,
    }
    return render(request, 'quiz_list_invite.html', context)


