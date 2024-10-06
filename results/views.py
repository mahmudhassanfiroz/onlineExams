from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Result, Feedback, Leaderboard
from liveExam.models import LiveExam, UserLiveExam
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import matplotlib.pyplot as plt
import io
import base64
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from results.models import Result
from exams.models import UserExam

@login_required
def results_overview(request):
    user_live_exam_content_type = ContentType.objects.get_for_model(UserLiveExam)
    user_exam_content_type = ContentType.objects.get_for_model(UserExam)

    results = Result.objects.filter(
        Q(content_type=user_live_exam_content_type, object_id__in=UserLiveExam.objects.filter(user=request.user).values_list('id', flat=True)) |
        Q(content_type=user_exam_content_type, object_id__in=UserExam.objects.filter(user=request.user).values_list('id', flat=True))
    ).order_by('-submission_time')

    total_exams = results.count()
    total_score = sum(result.score for result in results)
    total_correct = sum(result.correct_answers for result in results)
    total_wrong = sum(result.wrong_answers for result in results)

    context = {
        'total_exams': total_exams,
        'total_score': total_score,
        'total_correct': total_correct,
        'total_wrong': total_wrong,
    }
    return render(request, 'results/overview.html', context)

@login_required
def individual_result(request, result_id):
    result = get_object_or_404(Result, id=result_id, content_object__user=request.user)
    context = {'result': result}
    return render(request, 'results/individual_result.html', context)

@login_required
def result_analysis(request, result_id):
    result = get_object_or_404(Result, id=result_id, content_object__user=request.user)
    context = {'result': result}
    return render(request, 'results/result_analysis.html', context)

@login_required
def generate_pdf(request, result_id):
    result = get_object_or_404(Result, id=result_id, content_object__user=request.user)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content to the PDF
    p.drawString(100, 750, f"Result for {result.content_object.user.username}")
    if isinstance(result.content_object, UserLiveExam):
        p.drawString(100, 700, f"Live Exam: {result.content_object.live_exam.title}")
    else:
        p.drawString(100, 700, f"Exam: {result.content_object.exam.title}")
    p.drawString(100, 650, f"Score: {result.score}")
    p.drawString(100, 600, f"Correct Answers: {result.correct_answers}")
    p.drawString(100, 550, f"Wrong Answers: {result.wrong_answers}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def leaderboard(request, exam_id):
    exam = get_object_or_404(LiveExam, id=exam_id)
    leaderboard = Leaderboard.objects.filter(live_exam=exam).order_by('rank')
    context = {'leaderboard': leaderboard, 'exam': exam}
    return render(request, 'results/leaderboard.html', context)

@login_required
def result_comparison(request):
    results = Result.objects.filter(content_object__user=request.user).order_by('-submission_time')
    
    # Create a line chart
    plt.figure(figsize=(10, 5))
    plt.plot([result.submission_time for result in results], [result.score for result in results], marker='o')
    plt.title('Score Progression')
    plt.xlabel('Exam Date')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image to base64
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    context = {'results': results, 'graphic': graphic}
    return render(request, 'results/result_comparison.html', context)

@login_required
def submit_feedback(request, result_id):
    if request.method == 'POST':
        result = get_object_or_404(Result, id=result_id, content_object__user=request.user)
        comment = request.POST.get('comment')
        Feedback.objects.create(result=result, comment=comment)
        return redirect('results:individual_result', result_id=result_id)
    return redirect('results:individual_result', result_id=result_id)

