# Generated by Django 5.1.7 on 2025-03-18 07:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_profiles', '0002_hotel_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='owner',
        ),
        migrations.AddField(
            model_name='hotel',
            name='username',
            field=models.CharField(default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='hotel',
            name='name',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hotel', to=settings.AUTH_USER_MODEL),
        ),
    ]
