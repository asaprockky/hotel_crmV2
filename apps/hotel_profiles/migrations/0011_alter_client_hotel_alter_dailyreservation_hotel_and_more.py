# Generated by Django 5.1.7 on 2025-03-21 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_profiles', '0010_alter_room_room_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client', to='hotel_profiles.hotel'),
        ),
        migrations.AlterField(
            model_name='dailyreservation',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_reservations', to='hotel_profiles.hotel'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='hotel_profiles.hotel'),
        ),
        migrations.AlterField(
            model_name='room',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hotel_profiles.hotel'),
        ),
    ]
