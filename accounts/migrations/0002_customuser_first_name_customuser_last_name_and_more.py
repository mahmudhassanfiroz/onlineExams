# Generated by Django 5.1.1 on 2024-09-28 07:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='নামের প্রথম অংশ'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='নামের শেষ অংশ'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True, verbose_name='ব্যবহারকারীর নাম'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='mobile',
            field=models.CharField(blank=True, max_length=17, null=True, unique=True, validators=[django.core.validators.RegexValidator(message="মোবাইল নম্বর এই ফরম্যাটে হতে হবে: '+999999999'. সর্বোচ্চ 15 ডিজিট অনুমোদিত।", regex='^\\+?1?\\d{9,15}$')], verbose_name='মোবাইল নম্বর'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='name',
            field=models.CharField(max_length=255, verbose_name='পূর্ণ নাম'),
        ),
    ]
