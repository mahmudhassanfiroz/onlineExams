
# from django.utils import timezone
# from exams.models import ExamSchedule
# from services.models import Package

# def home(request):
#     featured_packages = Package.objects.filter(is_featured=True)
#     next_exam = ExamSchedule.objects.filter(exam_date__gt=timezone.now()).select_related('batch__category').order_by('exam_date').first()

#     if next_exam and next_exam.batch and next_exam.batch.category:
#         next_exam_category_id = next_exam.batch.category.id
#     else:
#         next_exam_category_id = None

#     context = {
#         'next_exam': next_exam,
#         'next_exam_category_id': next_exam_category_id,
#         'featured_packages': featured_packages,
#     }

#     return render(request, 'home.html', context)




# def about(request):
#     context = {
#         'title': 'আমাদের সম্পর্কে',
#         'mission': 'বাংলাদেশের যুব সমাজকে চাকরির জন্য প্রস্তুত করা',
#         'vision': 'প্রযুক্তির মাধ্যমে শিক্ষা ও কর্মসংস্থানের ক্ষেত্রে পরিবর্তন আনা',
#         'team_members': [
#             {'name': 'আব্দুল্লাহ', 'position': 'প্রতিষ্ঠাতা ও সিইও'},
#             {'name': 'ফাতেমা', 'position': 'প্রধান শিক্ষা বিশেষজ্ঞ'},
#             {'name': 'রহিম', 'position': 'প্রধান প্রযুক্তি কর্মকর্তা'},
#             {'name': 'নাজমা', 'position': 'HR বিশেষজ্ঞ'},
#         ],
#         'services': [
#             'বিভিন্ন ধরনের অনলাইন পরীক্ষা',
#             'লাইভ মক টেস্ট',
#             'বিষয়ভিত্তিক প্রশ্ন ব্যাংক',
#             'বিস্তারিত ফলাফল বিশ্লেষণ',
#             'ক্যারিয়ার কাউন্সেলিং',
#         ]
#     }
#     return render(request, 'about.html', context)

# views.py

# from django.shortcuts import render, redirect
# from django.core.mail import send_mail
# from django.contrib import messages

# def contact(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         subject = request.POST.get('subject')
#         message = request.POST.get('message')
        
        # এখানে ইমেইল পাঠানোর লজিক লিখুন
        # send_mail(
        #     subject,
        #     f"নাম: {name}\nইমেইল: {email}\n\nবার্তা:\n{message}",
        #     email,
        #     ['your-email@example.com'],  # আপনার ইমেইল ঠিকানা
        #     fail_silently=False,
        # )
        
        # ইমেইল পাঠানোর পরে, একটি সাকসেস মেসেজ দেখান
    #     messages.success(request, 'আপনার বার্তা সফলভাবে পাঠানো হয়েছে। আমরা শীঘ্রই আপনার সাথে যোগাযোগ করব।')
    #     return redirect('contact')
    
    # return render(request, 'contact.html')
