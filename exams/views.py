from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Exam, UserExam, UserAnswer, Question
from services.models import UserPackage

def exam_list(request):
    exams = Exam.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')

    if query:
        exams = exams.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        exams = exams.filter(exam_category__slug=category)
    if difficulty:
        exams = exams.filter(questions__difficulty_level=difficulty).distinct()

    context = {
        'exams': exams,
        'query': query,
        'selected_category': category,
        'selected_difficulty': difficulty,
    }
    return render(request, 'exams/exam_list.html', context)

@login_required
def exam_detail(request, slug):
    exam = get_object_or_404(Exam, slug=slug)
    user_package = UserPackage.objects.filter(user=request.user, package__exam_categories=exam.exam_category, is_active=True).first()
    can_take_exam = exam.is_free or (user_package is not None)

    context = {
        'exam': exam,
        'can_take_exam': can_take_exam,
    }
    return render(request, 'exams/exam_detail.html', context)

@login_required
def take_exam(request, slug):
    exam = get_object_or_404(Exam, slug=slug)
    questions = exam.questions.all()

    if request.method == 'POST':
        user_exam = UserExam.objects.create(user=request.user, exam=exam)
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            is_correct = answer == question.correct_answer
            UserAnswer.objects.create(
                user_exam=user_exam,
                question=question,
                answer_text=answer,
                is_correct=is_correct
            )
        user_exam.end_time = timezone.now()
        user_exam.is_completed = True
        user_exam.score = user_exam.useranswer_set.filter(is_correct=True).count()
        user_exam.save()
        return redirect('exams:exam_result', exam_id=user_exam.id)

    context = {
        'exam': exam,
        'questions': questions,
    }
    return render(request, 'exams/take_exam.html', context)

@login_required
def exam_result(request, exam_id):
    user_exam = get_object_or_404(UserExam, id=exam_id, user=request.user)
    answers = user_exam.useranswer_set.all().select_related('question')
    context = {
        'user_exam': user_exam,
        'answers': answers,
    }
    return render(request, 'exams/exam_result.html', context)

def free_exams(request):
    free_exams = Exam.objects.filter(is_free=True)
    context = {
        'exams': free_exams,
    }
    return render(request, 'exams/free_exams.html', context)

@login_required
def user_exams(request):
    user_exams = UserExam.objects.filter(user=request.user).order_by('-start_time')
    context = {
        'user_exams': user_exams,
    }
    return render(request, 'exams/user_exams.html', context)

