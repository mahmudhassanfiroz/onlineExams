

# from .models import Question, Answer

from exams.models import UserAnswer


def calculate_score(exam_session):
    total_questions = exam_session.exam.total_questions
    correct_answers = 0
    total_marks = 0
    
    answers = UserAnswer.objects.filter(session=exam_session).select_related('question')
    
    for answer in answers:
        question = answer.question
        if question.question_type == 'MCQ':
            if answer.selected_option == question.correct_option:
                correct_answers += 1
                total_marks += question.marks
        elif question.question_type == 'SHORT_ANSWER':
            # এখানে আপনি একটি NLP মডেল বা কীওয়ার্ড ম্যাচিং ব্যবহার করতে পারেন
            # এই উদাহরণে, আমরা সরল কীওয়ার্ড ম্যাচিং ব্যবহার করছি
            if any(keyword in answer.answer_text.lower() for keyword in question.keywords.lower().split(',')):
                correct_answers += 1
                total_marks += question.marks
        elif question.question_type == 'LONG_ANSWER':
            # দীর্ঘ উত্তরের প্রশ্নের জন্য, আমরা ধরে নিচ্ছি যে এগুলো ম্যানুয়ালি মূল্যায়ন করা হবে
            # তাই এখানে আমরা কোনো নম্বর যোগ করছি না
            pass
    
    percentage_score = (total_marks / (total_questions * exam_session.exam.marks_per_question)) * 100
    
    return {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'total_marks': total_marks,
        'percentage_score': round(percentage_score, 2)
    }

