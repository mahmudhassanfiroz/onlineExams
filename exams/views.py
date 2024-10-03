from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import ExamCategory, Batch, Question, ExamSchedule, ExamRegistration, ExamResult, ExamSettings, UserPerformance, MockExam, UserAnswer
from .forms import ExamRegistrationForm, ExamSettingsForm, QuestionForm

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import ExamCategory

def exam_category_list(request):
    category_list = ExamCategory.objects.all().order_by('name')
    
    # পেজিনেশন যোগ করা
    page = request.GET.get('page', 1)
    paginator = Paginator(category_list, 10)  # প্রতি পৃষ্ঠায় 10টি ক্যাটাগরি
    
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
        'title': 'পরীক্ষা ক্যাটাগরি তালিকা'
    }
    
    return render(request, 'exams/exam_category_list.html', context)

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .models import ExamCategory, Batch

def exam_category_detail(request, category_id):
    category = get_object_or_404(ExamCategory, pk=category_id)
    
    # ব্যাচগুলি ফিল্টার করা এবং অংশগ্রহণকারীদের সংখ্যা গণনা করা
    batches = Batch.objects.filter(category=category).annotate(
        participant_count=Count('participants')
    ).order_by('-start_date')
    
    # পেজিনেশন যোগ করা
    page = request.GET.get('page', 1)
    paginator = Paginator(batches, 10)  # প্রতি পৃষ্ঠায় 10টি ব্যাচ
    
    try:
        batches = paginator.page(page)
    except PageNotAnInteger:
        batches = paginator.page(1)
    except EmptyPage:
        batches = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'batches': batches,
        'category_id': category_id,
        'total_batches': batches.paginator.count,
        'title': f"{category.name} - বিস্তারিত"
    }
    
    return render(request, 'exams/category_detail.html', context)

def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    exam_schedules = ExamSchedule.objects.filter(batch=batch)
    context = {
        'batch': batch,
        'exam_schedules': exam_schedules,
        'title': f"{batch.name} - বিস্তারিত"
    }
    return render(request, 'exams/batch_detail.html', context)



@login_required
def exam_history(request):
    user_results = ExamResult.objects.filter(registration__user=request.user).order_by('-submitted_at')
    context = {
        'results': user_results,
        'title': 'পরীক্ষার ইতিহাস'
    }
    return render(request, 'exams/exam_history.html', context)

@login_required
def exam_confirmation(request, registration_id):
    registration = get_object_or_404(ExamRegistration, pk=registration_id)
    context = {
        'registration': registration,
        'title': 'পরীক্ষা রেজিস্ট্রেশন নিশ্চিতকরণ'
    }
    return render(request, 'exams/exam_confirmation.html', context)


@login_required
def exam_registration(request, exam_id):
    exam = get_object_or_404(ExamSchedule, pk=exam_id)
    if request.method == 'POST':
        form = ExamRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.exam = exam
            registration.save()
            # পেমেন্ট প্রসেস পেজে রিডাইরেক্ট করুন
            return redirect('payments:process_payment', item_type='exam', item_id=registration.id)
    else:
        form = ExamRegistrationForm()
    return render(request, 'exams/exam_registration.html', {'form': form, 'exam': exam})


from django.utils import timezone
from django.http import HttpResponseForbidden

@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(ExamSchedule, pk=exam_id)
    registration = get_object_or_404(ExamRegistration, user=request.user, exam=exam)
    
    if not registration.payment_status:
        messages.error(request, "আপনি এই পরীক্ষার জন্য পেমেন্ট করেননি।")
        return redirect('payments:process_payment', item_type='exam', item_id=registration.id)
    
    if timezone.now() < exam.exam_date:
        time_remaining = exam.exam_date - timezone.now()
        messages.warning(request, f"পরীক্ষা এখনও শুরু হয়নি। {time_remaining.days} দিন {time_remaining.seconds // 3600} ঘণ্টা বাকি আছে।")
        return redirect('exams:exam_details', exam_id=exam.id)
    
    if ExamResult.objects.filter(registration=registration).exists():
        messages.info(request, "আপনি ইতিমধ্যে এই পরীক্ষা দিয়েছেন।")
        return redirect('exams:exam_results', exam_id=exam.id)
    
    questions = Question.objects.filter(category=exam.batch.category).order_by('?')[:exam.examsettings.total_questions]
    
    if not questions:
        messages.error(request, "দুঃখিত, এই পরীক্ষার জন্য কোনো প্রশ্ন নেই।")
        return redirect('exams:exam_details', exam_id=exam.id)
    
    request.session['exam_start_time'] = timezone.now().isoformat()
    request.session['exam_questions'] = list(questions.values_list('id', flat=True))
    
    return render(request, 'exams/take_exam.html', {'exam': exam, 'questions': questions})


from django.db.models import Sum

@login_required
def submit_exam(request, exam_id):
    exam = get_object_or_404(ExamSchedule, pk=exam_id)
    registration = get_object_or_404(ExamRegistration, user=request.user, exam=exam)
    
    if request.method == 'POST':
        start_time = timezone.datetime.fromisoformat(request.session.get('exam_start_time'))
        end_time = timezone.now()
        duration = end_time - start_time
        
        if duration > exam.duration:
            return HttpResponseForbidden("পরীক্ষার সময় শেষ হয়ে গেছে।")
        
        score = 0
        for question_id, answer in request.POST.items():
            if question_id.startswith('q'):
                question = get_object_or_404(Question, pk=int(question_id[1:]))
                user_answer = UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                    exam_registration=registration,
                    answer_text=answer,
                    is_correct=(answer == question.correct_answer)
                )
                if user_answer.is_correct:
                    score += 1
        
        total_questions = exam.examsettings.total_questions
        percentage_score = (score / total_questions) * 100
        
        result = ExamResult.objects.create(
            registration=registration,
            score=score,
            pass_mark=exam.examsettings.pass_mark,
            submitted_at=end_time
        )
        
        return redirect('exam_result', result_id=result.id)
    
    return HttpResponseForbidden("অবৈধ অনুরোধ।")


@login_required
def exam_result_detail(request, result_id):
    result = get_object_or_404(ExamResult, pk=result_id, registration__user=request.user)
    user_answers = UserAnswer.objects.filter(exam_registration=result.registration)
    
    context = {
        'result': result,
        'user_answers': user_answers,
    }
    return render(request, 'exams/result_detail.html', context)

@login_required
def start_mock_exam(request, category_id):
    category = get_object_or_404(ExamCategory, pk=category_id)
    questions = Question.objects.filter(category=category).order_by('?')[:20]  # 20টি প্রশ্ন নিন
    
    mock_exam = MockExam.objects.create(user=request.user, exam_category=category)
    request.session['mock_exam_id'] = mock_exam.id
    request.session['mock_exam_questions'] = list(questions.values_list('id', flat=True))
    
    return render(request, 'exams/mock_exam.html', {'questions': questions, 'category': category})

@login_required
def submit_mock_exam(request):
    mock_exam_id = request.session.get('mock_exam_id')
    mock_exam = get_object_or_404(MockExam, pk=mock_exam_id, user=request.user)
    
    if request.method == 'POST':
        score = 0
        for question_id, answer in request.POST.items():
            if question_id.startswith('q'):
                question = get_object_or_404(Question, pk=int(question_id[1:]))
                if answer == question.correct_answer:
                    score += 1
        
        mock_exam.end_time = timezone.now()
        mock_exam.score = score
        mock_exam.save()
        
        return redirect('mock_exam_result', mock_exam_id=mock_exam.id)
    
    return HttpResponseForbidden("অবৈধ অনুরোধ।")

from django.db.models import Avg, Count

@login_required
def performance_analysis(request):
    user_performance = UserPerformance.objects.filter(user=request.user)
    exam_results = ExamResult.objects.filter(registration__user=request.user)
    
    category_performance = exam_results.values('registration__exam__batch__category__name').annotate(
        avg_score=Avg('score'),
        exam_count=Count('id')
    )
    
    context = {
        'user_performance': user_performance,
        'category_performance': category_performance,
    }
    return render(request, 'exams/performance_analysis.html', context)



@login_required
def create_question(request, category_id):
    category = get_object_or_404(ExamCategory, pk=category_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.category = category
            question.save()
            messages.success(request, 'নতুন প্রশ্ন সফলভাবে তৈরি করা হয়েছে।')
            return redirect('question_list', category_id=category_id)
    else:
        form = QuestionForm()
    return render(request, 'exams/question_form.html', {'form': form, 'category': category})

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'প্রশ্ন সফলভাবে আপডেট করা হয়েছে।')
            return redirect('question_list', category_id=question.category.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'exams/question_form.html', {'form': form, 'question': question})

@login_required
def question_list(request, category_id):
    category = get_object_or_404(ExamCategory, pk=category_id)
    questions = Question.objects.filter(category=category)
    return render(request, 'exams/question_list.html', {'questions': questions, 'category': category})





# @login_required
# def dashboard(request):
#     user_exams = ExamRegistration.objects.filter(user=request.user)
#     upcoming_exams = user_exams.filter(exam__exam_date__gt=timezone.now())
#     past_exams = user_exams.filter(exam__exam_date__lte=timezone.now())
#     results = ExamResult.objects.filter(registration__user=request.user)
    
#     context = {
#         'upcoming_exams': upcoming_exams,
#         'past_exams': past_exams,
#         'results': results,
#     }
#     return render(request, 'exams/dashboard.html', context)



@login_required
def exam_settings_create(request, exam_id):
    exam = get_object_or_404(ExamSchedule, pk=exam_id)
    if hasattr(exam, 'examsettings'):
        return redirect('exam_settings_update', exam_id=exam_id)
    
    if request.method == 'POST':
        form = ExamSettingsForm(request.POST)
        if form.is_valid():
            settings = form.save(commit=False)
            settings.exam = exam
            settings.save()
            messages.success(request, 'পরীক্ষার সেটিংস সফলভাবে তৈরি করা হয়েছে।')
            return redirect('exam_settings_detail', exam_id=exam_id)
    else:
        form = ExamSettingsForm()
    
    return render(request, 'exams/exam_settings_form.html', {'form': form, 'exam': exam})

@login_required
def exam_settings_detail(request, exam_id):
    exam = get_object_or_404(ExamSchedule, pk=exam_id)
    settings = get_object_or_404(ExamSettings, exam=exam)
    return render(request, 'exams/exam_settings_detail.html', {'settings': settings, 'exam': exam})

@login_required
def exam_settings_update(request, exam_id):
    exam = get_object_or_404(ExamSchedule, pk=exam_id)
    settings = get_object_or_404(ExamSettings, exam=exam)
    
    if request.method == 'POST':
        form = ExamSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'পরীক্ষার সেটিংস সফলভাবে আপডেট করা হয়েছে।')
            return redirect('exam_settings_detail', exam_id=exam_id)
    else:
        form = ExamSettingsForm(instance=settings)
    
    return render(request, 'exams/exam_settings_form.html', {'form': form, 'exam': exam})

@login_required
def exam_settings_delete(request, exam_id):
    exam = get_object_or_404(ExamSchedule, pk=exam_id)
    settings = get_object_or_404(ExamSettings, exam=exam)
    
    if request.method == 'POST':
        settings.delete()
        messages.success(request, 'পরীক্ষার সেটিংস সফলভাবে মুছে ফেলা হয়েছে।')
        return redirect('exam_schedule_detail', exam_id=exam_id)
    
    return render(request, 'exams/exam_settings_confirm_delete.html', {'settings': settings, 'exam': exam})

@login_required
def exam_settings_list(request):
    settings = ExamSettings.objects.all()
    return render(request, 'exams/exam_settings_list.html', {'settings': settings})