# Generated by Django 5.1.1 on 2024-10-06 11:18

import django_ckeditor_5.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='ad_type',
            field=models.CharField(choices=[('custom', 'কাস্টম বিজ্ঞাপন'), ('google', 'Google Ads')], default='custom', max_length=10, verbose_name='বিজ্ঞাপনের ধরন'),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='google_ad_code',
            field=models.TextField(blank=True, verbose_name='Google Ads কোড'),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='content',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='বিষয়বস্তু'),
        ),
    ]
