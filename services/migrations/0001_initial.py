# Generated by Django 5.1.1 on 2024-10-05 13:11

import django.db.models.deletion
import django_ckeditor_5.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', django_ckeditor_5.fields.CKEditor5Field()),
                ('image', models.ImageField(blank=True, null=True, upload_to='exam_categories/')),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', django_ckeditor_5.fields.CKEditor5Field()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration', models.DurationField()),
                ('package_type', models.CharField(choices=[('COACHING', 'কোচিং'), ('STUDENT', 'ছাত্র-ছাত্রী')], max_length=10)),
                ('is_featured', models.BooleanField(default=False)),
                ('exam_categories', models.ManyToManyField(to='services.examcategory')),
            ],
        ),
        migrations.CreateModel(
            name='UserPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_date', models.DateTimeField(auto_now_add=True)),
                ('expiry_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.package')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
