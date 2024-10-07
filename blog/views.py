from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib import messages
from django.utils.text import slugify
from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_POST
from django.utils import timezone

from accounts.models import CustomUser
from .models import Post, Tag, Comment, Reaction, Subscription
from .forms import PostForm, CommentForm, SubscriptionForm

def post_list(request, tag_slug=None):
    posts = Post.objects.filter(status='published', published_at__lte=timezone.now()).select_related('author').only('title', 'slug', 'author__username', 'published_at', 'content').order_by('-published_at')
    
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)
    
    featured_posts = Post.objects.filter(is_featured=True, status='published').select_related('author').only('title', 'slug', 'author__username', 'published_at')[:3]
    
    # Archive dates
    archive_dates = posts.annotate(month=TruncMonth('published_at')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('-month')

    archive_data = {}
    for date in archive_dates:
        year = date['month'].year
        month = date['month'].strftime('%B')
        if year not in archive_data:
            archive_data[year] = []
        archive_data[year].append({
            'name': month,
            'number': date['month'].strftime('%m'),
            'count': date['count']
        })

    archive_dates = [{'year': year, 'months': months} for year, months in archive_data.items()]
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    recent_posts = Post.objects.filter(status='published').select_related('author').only('title', 'slug', 'author__username', 'published_at').order_by('-published_at')[:5]
    
    tags = Tag.objects.annotate(post_count=Count('post'))
    
    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'tags': tags,
        'recent_posts': recent_posts,
        'archive_dates': archive_dates,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    post.views += 1
    post.save()
    
    comments = post.comments.filter(is_approved=True, parent=None).order_by('-created_at')
    related_posts = Post.objects.filter(tags__in=post.tags.all()).exclude(id=post.id).distinct()[:3]
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            messages.success(request, 'আপনার মন্তব্য সফলভাবে যোগ করা হয়েছে।')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # স্লাগ তৈরি
            base_slug = slugify(post.title)
            unique_slug = base_slug
            num = 1
            while Post.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            post.slug = unique_slug
            
            if 'image' in request.FILES:
                post.image = request.FILES['image']
            
            try:
                post.save()
                form.save_m2m()  # ট্যাগ সেভ করা
                messages.success(request, 'আপনার পোস্ট সফলভাবে তৈরি করা হয়েছে।')
                return redirect('blog:post_list')  # ব্লগের মূল পেজে রিডাইরেক্ট
            except Exception as e:
                messages.error(request, f'পোস্ট সেভ করতে সমস্যা: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PostForm()
    
    return render(request, 'blog/create_post.html', {'form': form})


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            if updated_post.status == 'published' and not post.published_at:
                updated_post.published_at = timezone.now()
            updated_post.save()
            form.save_m2m()
            messages.success(request, 'আপনার পোস্ট সফলভাবে আপডেট করা হয়েছে।')
            return redirect('blog:post_detail', slug=updated_post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'আপনার পোস্ট সফলভাবে মুছে ফেলা হয়েছে।')
        return redirect('blog:post_list')
    
    return render(request, 'blog/delete_post.html', {'post': post})

@login_required
def react_to_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        reaction_type = request.POST.get('reaction_type')
        
        reaction, created = Reaction.objects.get_or_create(user=user, post=post)
        
        if not created and reaction.reaction_type == reaction_type:
            reaction.delete()
            action = 'removed'
        else:
            reaction.reaction_type = reaction_type
            reaction.save()
            action = 'added'
        
        reaction_counts = post.reactions.values('reaction_type').annotate(count=Count('id'))
        
        return JsonResponse({
            'action': action,
            'reaction_counts': dict(reaction_counts),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def share_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.shares += 1
        post.save()
        return JsonResponse({'shares': post.shares})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'আপনি সফলভাবে সাবস্ক্রাইব করেছেন।')
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = SubscriptionForm()
    
    return render(request, 'blog/subscribe.html', {'form': form})

def tag_list(request):
    tags = Tag.objects.annotate(post_count=Count('post'))
    return render(request, 'blog/tag_list.html', {'tags': tags})

def author_posts(request, username):
    author = get_object_or_404(CustomUser, username=username)
    posts = Post.objects.filter(author=author, status='published').order_by('-published_at')
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'blog/author_posts.html', {'author': author, 'posts': posts})

def archive(request, year, month):
    posts = Post.objects.filter(status='published', published_at__year=year, published_at__month=month).order_by('-published_at')
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'blog/archive.html', {'posts': posts, 'year': year, 'month': month})

@login_required
@require_POST
def interact_with_post(request):
    post_id = request.POST.get('post_id')
    action = request.POST.get('action')
    
    post = get_object_or_404(Post, id=post_id)
    if action == 'like':
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    elif action == 'share':
        post.shares += 1
        post.save()
    
    return JsonResponse({
        'likes': post.total_likes(),
        'shares': post.shares,
    })

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content')
    comment = Comment.objects.create(post=post, user=request.user, content=content)
    return JsonResponse({
        'status': 'success',
        'comment_id': comment.id,
        'user': comment.user.username,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%B %d, %Y %H:%M')
    })

