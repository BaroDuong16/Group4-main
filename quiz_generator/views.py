from django.shortcuts import render, redirect
from .models import Question, QuizBank
from .forms import QuestionGenerationForm
from .utils import generate_mcq, calculate_similarity

def generate_question(request):
    if request.method == "POST":
        form = QuestionGenerationForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data["topic"]
            question_text = generate_mcq(topic)

            # Check similarity with existing questions in the quiz bank
            all_questions = Question.objects.all()
            highest_similarity = 0
            for q in all_questions:
                similarity = calculate_similarity(question_text, q.text)
                if similarity > highest_similarity:
                    highest_similarity = similarity

            # Suggest adding to the bank if similarity is below 0.7
            if highest_similarity < 0.7:
                question = Question.objects.create(text=question_text, correct_answer="Answer Placeholder")
                QuizBank.objects.create(question=question, similarity_score=highest_similarity)
                advice = "This question is unique enough. Would you like to add it to the quiz bank?"
            else:
                advice = "This question is too similar to existing questions."

            return render(request, "question_result.html", {"question": question_text, "advice": advice})
    else:
        form = QuestionGenerationForm()

    return render(request, "generate_question.html", {"form": form})
