from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import LiveExam, UserLiveExam, LiveExamAnswer
from services.models import UserPackage

def live_exam_list(request):
    live_exams = LiveExam.objects.filter(exam_date__gte=timezone.now().date()).order_by('exam_date', 'start_time')
    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        live_exams = live_exams.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        live_exams = live_exams.filter(exam_category__slug=category)

    context = {
        'live_exams': live_exams,
        'query': query,
        'selected_category': category,
    }
    return render(request, 'liveExam/live_exam_list.html', context)

@login_required
def live_exam_detail(request, slug):
    live_exam = get_object_or_404(LiveExam.objects.select_related('exam_category'), slug=slug)
    user_package = UserPackage.objects.filter(user=request.user, package__exam_categories=live_exam.exam_category, is_active=True).first()
    can_take_exam = live_exam.is_free or (user_package is not None)

    context = {
        'live_exam': live_exam,
        'can_take_exam': can_take_exam,
    }
    return render(request, 'liveExam/live_exam_detail.html', context)

@login_required
def take_live_exam(request, slug):
    live_exam = get_object_or_404(LiveExam, slug=slug)
    user_package = UserPackage.objects.filter(user=request.user, package__exam_categories=live_exam.exam_category, is_active=True).first()
    
    if not live_exam.is_free and not user_package:
        messages.error(request, 'আপনার এই লাইভ পরীক্ষা দেওয়ার অনুমতি নেই। অনুগ্রহ করে প্যাকেজ কিনুন।')
        return redirect('liveExam:package_list')

    if not live_exam.is_active():
        messages.error(request, 'এই লাইভ পরীক্ষা এখন চলমান নয়।')
        return redirect('liveExam:live_exam_detail', slug=slug)

    if request.method == 'POST':
        user_live_exam = UserLiveExam.objects.create(user=request.user, live_exam=live_exam)
        for question in live_exam.questions.all():
            answer = request.POST.get(f'question_{question.id}')
            is_correct = answer == question.correct_answer
            LiveExamAnswer.objects.create(
                user_live_exam=user_live_exam,
                question=question,
                answer_text=answer,
                is_correct=is_correct
            )
        user_live_exam.end_time = timezone.now()
        user_live_exam.is_completed = True
        user_live_exam.score = sum(answer.is_correct for answer in user_live_exam.liveexamanswer_set.all())
        user_live_exam.save()
        return redirect('liveExam:live_exam_result', exam_id=user_live_exam.id)

    context = {
        'live_exam': live_exam,
        'questions': live_exam.questions.all(),
    }
    return render(request, 'liveExam/take_live_exam.html', context)

@login_required
def live_exam_result(request, exam_id):
    user_live_exam = get_object_or_404(UserLiveExam.objects.select_related('live_exam'), id=exam_id, user=request.user)
    context = {
        'user_live_exam': user_live_exam,
        'answers': user_live_exam.liveexamanswer_set.all(),
    }
    return render(request, 'liveExam/live_exam_result.html', context)

def free_live_exams(request):
    free_live_exams = LiveExam.objects.filter(is_free=True, exam_date__gte=timezone.now().date()).order_by('exam_date', 'start_time')
    context = {
        'live_exams': free_live_exams,
    }
    return render(request, 'liveExam/free_live_exams.html', context)

@login_required
def user_live_exams(request):
    user_live_exams = UserLiveExam.objects.filter(user=request.user).order_by('-start_time').select_related('live_exam')
    context = {
        'user_live_exams': user_live_exams,
    }
    return render(request, 'liveExam/user_live_exams.html', context)
