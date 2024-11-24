
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from django.contrib import admin
from user.models import User
from .models import Quiz, Question, AnswerOption, StudentQuizAttempt
from course.models import Course

# Quiz Resource
class QuizResource(resources.ModelResource):
    created_by = fields.Field(
        column_name='created_by__username',  # Assuming username is the desired attribute to import/export
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')  # Use the username to link to the User model
    )
    
    course = fields.Field(
        column_name='course__course_name',  # Assuming course_name is the desired attribute to import/export
        attribute='course',
        widget=ForeignKeyWidget(Course, 'course_name')  # Use the course name to link to the Course model
    )

    class Meta:
        model = Quiz
        fields = ('id', 'course', 'quiz_title', 'quiz_description', 'total_marks', 'time_limit',
                  'created_by', 'created_at', 'updated_at', 'start_datetime', 'end_datetime', 'attempts_allowed')

# Admin registration for Quiz
@admin.register(Quiz)
class QuizAdmin(ImportExportModelAdmin):
    resource_class = QuizResource
    list_display = ('quiz_title', 'course', 'created_by', 'created_at', 'updated_at')
    search_fields = ('quiz_title', 'course__course_name', 'created_by__username')
    list_filter = ('course', 'created_by')

# Question Resource
class QuestionResource(resources.ModelResource):
    quiz = fields.Field(
        column_name='quiz__quiz_title',  # Assuming quiz_title is the desired attribute to import/export
        attribute='quiz',
        widget=ForeignKeyWidget(Quiz, 'quiz_title')  # Use the quiz title to link to the Quiz model
    )

    class Meta:
        model = Question
        fields = ('id', 'quiz', 'question_text', 'question_type', 'points')

# Admin registration for Question
@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ('question_text', 'quiz', 'question_type', 'points')
    search_fields = ('question_text', 'quiz__quiz_title')
    list_filter = ('quiz', 'question_type')


# AnswerOption Resource
class AnswerOptionResource(resources.ModelResource):
    question = fields.Field(
        column_name='question__question_text',  # Assuming question_text is the desired attribute to import/export
        attribute='question',
        widget=ForeignKeyWidget(Question, 'question_text')  # Use the question text to link to the Question model
    )

    class Meta:
        model = AnswerOption
        fields = ('id', 'question', 'option_text', 'is_correct')

# Admin registration for AnswerOption
@admin.register(AnswerOption)
class AnswerOptionAdmin(ImportExportModelAdmin):
    resource_class = AnswerOptionResource
    list_display = ('option_text', 'question', 'is_correct')
    search_fields = ('option_text', 'question__question_text')
    list_filter = ('question', 'is_correct')


# StudentQuizAttempt Resource
class StudentQuizAttemptResource(resources.ModelResource):
    user = fields.Field(
        column_name='user__username',  # Assuming username is the desired attribute to import/export
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')  # Use the username to link to the User model
    )
    
    quiz = fields.Field(
        column_name='quiz__quiz_title',  # Assuming quiz_title is the desired attribute to import/export
        attribute='quiz',
        widget=ForeignKeyWidget(Quiz, 'quiz_title')  # Use the quiz title to link to the Quiz model
    )

    class Meta:
        model = StudentQuizAttempt
        fields = ('id', 'user', 'quiz', 'score', 'attempt_date', 'is_proctored')

# Admin registration for StudentQuizAttempt
@admin.register(StudentQuizAttempt)
class StudentQuizAttemptAdmin(ImportExportModelAdmin):
    resource_class = StudentQuizAttemptResource
    list_display = ('user', 'quiz', 'score', 'attempt_date', 'is_proctored')
    search_fields = ('user__username', 'quiz__quiz_title')
    list_filter = ('quiz', 'is_proctored')


