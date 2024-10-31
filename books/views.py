from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone

from accounts.models import CustomUser
from payments.models import Payment
from .models import Book, Category, Author, Wishlist, BookReview
from .forms import ReviewForm

def book_list(request):
    search_query = request.GET.get('search')
    category_id = request.GET.get('category')
    
    books = Book.objects.all()
    if search_query:
        books = books.filter(title__icontains=search_query) | books.filter(author__name__icontains=search_query)
    
    if category_id:
        books = books.filter(category_id=category_id)

    context = {
        'books': books,
        'categories': Category.objects.all(),
        'featured_books': Book.objects.filter(is_featured=True),
    }
    return render(request, 'books/book_list.html', context)

@login_required
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
            messages.success(request, 'আপনার রিভিউ সফলভাবে যোগ করা হয়েছে।')
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
    if created:
        messages.success(request, 'বইটি আপনার উইশলিস্টে যোগ করা হয়েছে।')
    else:
        messages.info(request, 'বইটি ইতিমধ্যে আপনার উইশলিস্টে আছে।')
    return JsonResponse({'status': 'success'})

@login_required
def remove_from_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    deleted, _ = Wishlist.objects.filter(user=request.user, book=book).delete()
    if deleted:
        messages.success(request, 'বইটি আপনার উইশলিস্ট থেকে সরানো হয়েছে।')
    else:
        messages.error(request, 'বইটি আপনার উইশলিস্টে পাওয়া যায়নি।')
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

@login_required
def purchase_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if book.is_free:
        messages.success(request, 'আপনি সফলভাবে বিনামূল্যে বইটি পেয়েছেন!')
        return redirect('books:download_book', book_id=book.id)
    
    try:
        payment = Payment.objects.create(
            user=request.user,
            amount=book.price,
            payment_type='BOOK',
            status='PENDING',
            tran_id=f"BOOK-{book.id}-{timezone.now().timestamp()}",
            book=book
        )
        return redirect('payments:initiate_payment', item_type='BOOK', item_id=book.id)
    except Exception as e:
        messages.error(request, f'পেমেন্ট তৈরি করতে সমস্যা হয়েছে: {str(e)}')
        return redirect('books:book_detail', book_id=book.id)

@login_required
def download_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    payment = Payment.objects.filter(user=request.user, book=book, status='COMPLETED').first()
    
    if payment or book.is_free:
        if book.pdf_file:
            response = HttpResponse(book.pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'
            return response
        else:
            messages.error(request, 'বইয়ের PDF ফাইল পাওয়া যায়নি।')
    else:
        messages.error(request, 'আপনি এই বইটি কিনেন নি।')
    
    return redirect('books:book_detail', book_id=book.id)
