# Generated by Django 4.2.17 on 2025-01-11 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_booking_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='user',
        ),
    ]
