from django.utils import timezone
from django.views.generic import ListView

from exams.models import ExamRegistration, Question, UserAnswer
from .models import LiveExam

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F, ExpressionWrapper, DateTimeField
from django.shortcuts import render

def live_exam_list(request):
    now = timezone.now()
    tomorrow = now + timezone.timedelta(days=1)
    
    live_exams = LiveExam.objects.annotate(
        end_time=ExpressionWrapper(
            F('exam_date') + F('start_time') + F('duration'),
            output_field=DateTimeField()
        )
    ).filter(
        end_time__gte=now,
        exam_date__lte=tomorrow.date()
    ).order_by('exam_date', 'start_time')
    
    paginator = Paginator(live_exams, 10)
    page = request.GET.get('page')
    
    try:
        live_exams = paginator.page(page)
    except PageNotAnInteger:
        live_exams = paginator.page(1)
    except EmptyPage:
        live_exams = paginator.page(paginator.num_pages)
    
    context = {
        'live_exams': live_exams
    }
    return render(request, 'liveExam/live_exam_list.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import LiveExam

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(LiveExam, id=exam_id)
    
    # পরীক্ষা শুরু হওয়ার আগে বিস্তারিত দেখার অনুমতি দিন
    if exam.start_time > timezone.now():
        is_registered = ExamRegistration.objects.filter(exam=exam, user=request.user).exists()
        can_register = not is_registered and exam.registration_deadline > timezone.now()
        
        context = {
            'exam': exam,
            'is_registered': is_registered,
            'can_register': can_register,
            'time_until_start': exam.start_time - timezone.now(),
        }
        return render(request, 'liveExam/exam_detail.html', context)
    
    # পরীক্ষা চলাকালীন, শুধুমাত্র নিবন্ধিত ব্যবহারকারীদের অনুমতি দিন
    elif exam.start_time <= timezone.now() < exam.end_time:
        if ExamRegistration.objects.filter(exam=exam, user=request.user).exists():
            context = {
                'exam': exam,
                'time_remaining': exam.end_time - timezone.now(),
            }
            return render(request, 'liveExam/exam_in_progress.html', context)
        else:
            return HttpResponseForbidden("আপনি এই পরীক্ষায় নিবন্ধিত নন।")
    
    # পরীক্ষা শেষ হওয়ার পর ফলাফল দেখান
    else:
        if ExamRegistration.objects.filter(exam=exam, user=request.user).exists():
            # এখানে পরীক্ষার ফলাফল লজিক যোগ করুন
            context = {
                'exam': exam,
                'result': "পরীক্ষার ফলাফল এখানে দেখানো হবে",
            }
            return render(request, 'liveExam/exam_result.html', context)
        else:
            return HttpResponseForbidden("আপনি এই পরীক্ষায় অংশগ্রহণ করেননি।")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import LiveExam
from .forms import ExamRegistrationForm

@login_required
def exam_confirmation(request, exam_id):
    exam = get_object_or_404(LiveExam, id=exam_id)
    user = request.user

    # চেক করুন যে পরীক্ষার নিবন্ধন এখনও খোলা আছে কিনা
    if exam.registration_deadline < timezone.now():
        messages.error(request, "দুঃখিত, এই পরীক্ষার নিবন্ধনের সময়সীমা শেষ হয়ে গেছে।")
        return redirect('exam_detail', exam_id=exam.id)

    # চেক করুন যে ব্যবহারকারী ইতিমধ্যে নিবন্ধিত কিনা
    if ExamRegistration.objects.filter(exam=exam, user=user).exists():
        messages.info(request, "আপনি ইতিমধ্যে এই পরীক্ষার জন্য নিবন্ধিত।")
        return redirect('exam_detail', exam_id=exam.id)

    if request.method == 'POST':
        form = ExamRegistrationForm(request.POST)
        if form.is_valid():
            # নিবন্ধন তৈরি করুন
            registration = ExamRegistration(
                exam=exam,
                user=user,
                agreed_to_terms=form.cleaned_data['agreed_to_terms']
            )
            registration.save()

            messages.success(request, f"আপনি সফলভাবে '{exam.title}' পরীক্ষার জন্য নিবন্ধন করেছেন।")
            return redirect('exam_detail', exam_id=exam.id)
    else:
        form = ExamRegistrationForm()

    context = {
        'exam': exam,
        'form': form,
    }
    return render(request, 'liveExam/exam_confirmation.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import LiveExam, ExamSession
# from django.db import transaction

@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(LiveExam, id=exam_id)
    user = request.user

    if not exam.is_active():
        return HttpResponseForbidden("পরীক্ষা এখনও শুরু হয়নি বা শেষ হয়ে গেছে।")

    # চেক করুন যে ব্যবহারকারী নিবন্ধিত কিনা
    if not ExamRegistration.objects.filter(exam=exam, user=user).exists():
        return HttpResponseForbidden("আপনি এই পরীক্ষায় নিবন্ধিত নন।")

    # চেক করুন যে ব্যবহারকারী ইতিমধ্যে পরীক্ষা শুরু করেছে কিনা
    exam_session = ExamSession.objects.filter(exam=exam, user=user).first()

    if exam_session:
        # যদি সেশন থাকে, তবে চলমান পরীক্ষায় ফিরে যান
        return redirect('liveExam:continue_exam', session_id=exam_session.id)

    # নতুন পরীক্ষা সেশন তৈরি করুন
    with transaction.atomic():
        exam_session = ExamSession.objects.create(
            exam=exam,
            user=user,
            start_time=timezone.now(),
            end_time=timezone.now() + exam.duration
        )

        # পরীক্ষার জন্য প্রশ্ন লোড করুন
        questions = Question.objects.filter(exam=exam).order_by('?')[:exam.total_questions]
        for question in questions:
            UserAnswer.objects.create(session=exam_session, question=question)

    return redirect('liveExam:continue_exam', session_id=exam_session.id)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from .models import LiveExam, ExamSession
from .utils import calculate_score  # এই ফাংশনটি আপনাকে নিজে লিখতে হবে

@login_required
def submit_exam(request, session_id):
    exam_session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    
    if exam_session.is_completed:
        messages.warning(request, "এই পরীক্ষা ইতিমধ্যে জমা দেওয়া হয়েছে।")
        return redirect('exam_result', session_id=session_id)
    
    if request.method == 'POST':
        with transaction.atomic():
            # সব উত্তর আপডেট করুন
            for answer in exam_session.answers.all():
                answer_text = request.POST.get(f'question_{answer.question.id}')
                if answer_text:
                    answer.answer_text = answer_text
                    answer.save()
            
            # পরীক্ষা সেশন বন্ধ করুন
            exam_session.is_completed = True
            exam_session.end_time = timezone.now()
            exam_session.save()
            
            # স্কোর গণনা করুন
            score = calculate_score(exam_session)
            exam_session.score = score
            exam_session.save()
        
        messages.success(request, "আপনার পরীক্ষা সফলভাবে জমা দেওয়া হয়েছে।")
        return redirect('exam_result', session_id=session_id)
    
    # GET রিকোয়েস্টের জন্য, পরীক্ষার সারাংশ দেখান
    questions = Question.objects.filter(exam=exam_session.exam)
    answers = UserAnswer.objects.filter(session=exam_session)
    
    context = {
        'exam_session': exam_session,
        'questions': questions,
        'answers': answers,
    }
    return render(request, 'liveExam/submit_exam.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LiveExam

@login_required
def exam_registration(request, exam_id):
    exam = LiveExam.objects.get(pk=exam_id)
    if request.method == 'POST':
        ExamRegistration.objects.create(user=request.user, live_exam=exam)
        # এখানে নোটিফিকেশন লজিক যোগ করুন
        return redirect('exam_confirmation')
    return render(request, 'liveExam/exam_registration.html', {'exam': exam})

from django.shortcuts import render
from .models import LiveExam

def exam_interface(request, exam_id):
    exam = LiveExam.objects.get(pk=exam_id)
    questions = Question.objects.filter(exam=exam)
    return render(request, 'liveExam/exam_interface.html', {'exam': exam, 'questions': questions})

from django.http import JsonResponse

def submit_answer(request):
    if request.method == 'POST' and request.is_ajax():
        question_id = request.POST.get('question_id')
        answer_id = request.POST.get('answer_id')
        # এখানে উত্তর সংরক্ষণের লজিক যোগ করুন
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def exam_result(request, exam_id):
    exam = LiveExam.objects.get(pk=exam_id)
    user_answers = UserAnswer.objects.filter(user=request.user, question__exam=exam)
    correct_answers = user_answers.filter(is_correct=True).count()
    total_questions = exam.question_set.count()
    score = (correct_answers / total_questions) * 100

    return render(request, 'liveExam/exam_result.html', {
        'exam': exam,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions
    })

def performance_review(request, exam_id):
    exam = LiveExam.objects.get(pk=exam_id)
    user_answers = UserAnswer.objects.filter(user=request.user, question__exam=exam)
    
    return render(request, 'liveExam/performance_review.html', {
        'exam': exam,
        'user_answers': user_answers
    })

def exam_status(request, exam_id):
    exam = get_object_or_404(LiveExam, id=exam_id)
    now = timezone.now()
    exam_start = timezone.make_aware(timezone.datetime.combine(exam.exam_date, exam.start_time))
    exam_end = exam_start + exam.duration

    has_started = now >= exam_start
    is_ongoing = exam_start <= now < exam_end

    if has_started:
        if is_ongoing:
            time_remaining = str(exam_end - now).split('.')[0]
        else:
            time_remaining = "00:00:00"
    else:
        time_remaining = str(exam_start - now).split('.')[0]

    return JsonResponse({
        'has_started': has_started,
        'is_ongoing': is_ongoing,
        'time_until_start': str(exam_start - now).split('.')[0] if not has_started else "00:00:00",
        'time_remaining': time_remaining
    })

