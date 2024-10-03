# Generated by Django 5.1.1 on 2024-09-27 02:41

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='নাম')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='ইমেইল ঠিকানা')),
                ('mobile', models.CharField(blank=True, max_length=17, null=True, unique=True, validators=[django.core.validators.RegexValidator(message="মোবাইল নম্বর এই ফরম্যাটে হতে হবে: '+999999999'. সর্বোচ্চ 15 ডিজিট অনুমোদিত।", regex='^\\+?1?\\d{9,15}$')])),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/', verbose_name='প্রোফাইল ছবি')),
                ('is_staff', models.BooleanField(default=False, verbose_name='স্টাফ স্ট্যাটাস')),
                ('is_active', models.BooleanField(default=True, verbose_name='সক্রিয়')),
                ('is_email_verified', models.BooleanField(default=False, verbose_name='ইমেইল যাচাইকৃত')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='যোগদানের তারিখ')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='শেষ লগইন')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'ব্যবহারকারী',
                'verbose_name_plural': 'ব্যবহারকারীগণ',
                'ordering': ['-date_joined'],
            },
        ),
        migrations.CreateModel(
            name='LoginHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_datetime', models.DateTimeField(auto_now_add=True, verbose_name='লগইন সময়')),
                ('ip_address', models.GenericIPAddressField(verbose_name='আইপি ঠিকানা')),
                ('user_agent', models.TextField(verbose_name='ইউজার এজেন্ট')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'লগইন ইতিহাস',
                'verbose_name_plural': 'লগইন ইতিহাসসমূহ',
                'ordering': ['-login_datetime'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500, verbose_name='জীবনী')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='জন্ম তারিখ')),
                ('location', models.CharField(blank=True, max_length=30, verbose_name='অবস্থান')),
                ('website', models.URLField(blank=True, max_length=100, verbose_name='ওয়েবসাইট')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ব্যবহারকারী প্রোফাইল',
                'verbose_name_plural': 'ব্যবহারকারী প্রোফাইলসমূহ',
            },
        ),
    ]
