# Generated by Django 5.1.1 on 2024-10-06 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_advertisement_ad_type_advertisement_google_ad_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='শিরোনাম'),
        ),
    ]
