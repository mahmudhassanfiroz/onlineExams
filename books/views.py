from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse

from accounts.models import CustomUser
from exams.models import ExamRegistration
from payments.forms import PaymentForm
from payments.models import Payment, PurchaseHistory
from payments.views import process_payment, send_payment_confirmation_email
from .models import Book, Category, Author, Wishlist
from .forms import ReviewForm
from django.contrib import messages
from django.utils import timezone


def book_list(request):
    books = Book.objects.all()
    categories = Category.objects.all()
    featured_books = Book.objects.filter(is_featured=True)
    
    search_query = request.GET.get('search')
    category_id = request.GET.get('category')
    
    if search_query:
        books = books.filter(title__icontains=search_query) | books.filter(author__name__icontains=search_query)
    
    if category_id:
        books = books.filter(category_id=category_id)
    
    context = {
        'books': books,
        'categories': categories,
        'featured_books': featured_books,
    }
    return render(request, 'books/book_list.html', context)

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.book_reviews.all()
    average_rating = book.book_reviews.aggregate(Avg('rating'))['rating__avg']
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('books:book_detail', book_id=book.id)
    else:
        form = ReviewForm()
    
    context = {
        'book': book,
        'reviews': reviews,
        'avg_rating': average_rating,
        'form': form,
    }
    return render(request, 'books/book_detail.html', context)



@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, book=book)
    return JsonResponse({'status': 'success'})

@login_required
def remove_from_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.filter(user=request.user, book=book).delete()
    return JsonResponse({'status': 'success'})

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {'wishlist_items': wishlist_items}
    return render(request, 'books/wishlist.html', context)

def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    books = Book.objects.filter(author=author)
    context = {'author': author, 'books': books}
    return render(request, 'books/author_detail.html', context)

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'books/category_list.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    books = Book.objects.filter(category=category)
    context = {'category': category, 'books': books}
    return render(request, 'books/category_detail.html', context)

def create_order(user, book):
    return Payment.objects.create(
        user=user,
        book=book,
        price=book.price,
        status='pending'
    )

@login_required
def purchase_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if book.is_free:
        PurchaseHistory.objects.create(user=request.user, book=book)
        messages.success(request, 'আপনি সফলভাবে বিনামূল্যে বইটি পেয়েছেন!')
        return redirect('books:download_book', book_id=book.id)
    
    # পেমেন্ট অবজেক্ট আপডেট করুন বা তৈরি করুন
    payment, created = Payment.objects.update_or_create(
        user=request.user,
        book=book,
        status='pending',
        defaults={
            'amount': book.price,
            'created_at': timezone.now()  # পেমেন্টের সময় আপডেট করুন
        }
    )
    
    # পেমেন্ট প্রসেস করার জন্য রিডাইরেক্ট করুন
    return redirect('payments:process_payment', item_type='book', item_id=book.id)

@login_required
def download_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    purchase = PurchaseHistory.objects.filter(user=request.user, book=book).first()
    
    if purchase or book.is_free:
        response = HttpResponse(book.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'
        return response
    else:
        messages.error(request, 'আপনি এই বইটি কিনেন নি।')
        return redirect('books:book_detail', book_id=book.id)
    
    