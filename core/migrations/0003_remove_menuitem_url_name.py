# Generated by Django 5.1.1 on 2024-10-02 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_menuitem_url_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuitem',
            name='url_name',
        ),
    ]
