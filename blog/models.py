from django.db import models
from accounts.models import CustomUser
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from tinymce.models import HTMLField
from django.utils import timezone
from django.urls import reverse
# from django.contrib.auth.models import User


def generate_unique_slug(model_instance, slugable_field_name, slug_field_name):
    """
    :param model_instance: model instance for which slug is being created
    :param slugable_field_name: name of the field from which slug is generated
    :param slug_field_name: name of the slug field
    :return: unique slug
    """
    slug = slugify(getattr(model_instance, slugable_field_name))
    unique_slug = slug
    extension = 1
    ModelClass = model_instance.__class__

    while ModelClass._default_manager.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = '{}-{}'.format(slug, extension)
        extension += 1
    
    return unique_slug


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'খসড়া'),
        ('published', 'প্রকাশিত'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = HTMLField()
    summary = models.TextField(max_length=300, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)
    shares = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, 'title', 'slug')
        if not self.summary:
            self.summary = self.content[:300]
        if not self.slug:  # এই লাইনটি যোগ করুন
            self.slug = slugify(self.title)  # এই লাইনটি যোগ করুন
        super().save(*args, **kwargs)

    def publish(self):
        self.published_at = timezone.now()
        self.status = 'published'
        self.save()

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # অটো-অ্যাপ্রুভ করার জন্য
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ('user', 'post')


class Subscription(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

