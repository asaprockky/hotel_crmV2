# Generated by Django 5.1.7 on 2025-03-21 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_profiles', '0008_alter_client_hotel_alter_reservation_hotel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyreservation',
            name='profit',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
