from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.utils import timezone
from django.db.models import Q
ROOM_STATUS_CHOICES = [
    ('available', 'Available'),
    ('unavailable', 'Unavailable'),
    ('reserved', 'Reserved')
]

HOTEL_PLAN_CHOICES = [
    ('basic', 'Basic'),
    ('standard', 'Standard'),
    ('premium', 'Premium')
]
class Hotel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="hotel")
    bio = models.TextField(max_length=500, blank=True)
    date_registered = models.DateField(auto_now_add=True)
    balance = models.DecimalField(max_digits=10,decimal_places=0, default=0)
    plan = models.TextField(max_length= 10, choices=HOTEL_PLAN_CHOICES, default= "basic")
    last_payment = models.DateField(blank= True, null= True)
    

    def __str__(self):
        return self.user.username

class TgId(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, related_name="tgid")
    
    POSITION_CHOICES = [
        ('staff', 'Staff'),
        ('boss', 'Boss'),
    ]
    position = models.CharField(max_length=7, choices=POSITION_CHOICES, null=True, blank=True)
    tg_id = models.DecimalField(max_digits=15, decimal_places=0, null=True, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['hotel'],
                condition=Q(position='staff'),
                name='unique_staff_per_hotel'
            ),
            models.UniqueConstraint(
                fields=['hotel'],
                condition=Q(position='boss'),
                name='unique_boss_per_hotel'
            )
        ]
class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=6)
    room_type = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.CharField(max_length= 15, choices= ROOM_STATUS_CHOICES, default= "available" )
    

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"
class Plan(models.Model):
    key = models.CharField(max_length=20, choices=HOTEL_PLAN_CHOICES, unique=True)
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField(help_text="Narx so'mda (UZS)")
    description = models.TextField(blank=True)
    max_rooms = models.PositiveIntegerField()
    telegram_notifications = models.BooleanField(default=True)
    financial_reports = models.BooleanField(default=False)
    export_excel = models.BooleanField(default=False)
    multi_hotel = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.price} UZS/oy)"
    
    
class Client(models.Model):
    full_name = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=10, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default= 1)
    def __str__(self):
        return f"{self.full_name} ({self.passport_number})"

    def deduct_balance(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

class Reservation(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reservations")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="reservations")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservations")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    check_in = models.DateField()
    check_out = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.room:
            today = timezone.localdate()
            print(today)
            if self.check_in == today:
                self.room.is_available = 'unavailable'  # Use valid choice
                self.room.save()
            elif self.check_in > today:
                self.room.is_available = 'reserved'  # Use valid choice
                self.room.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.room:
            has_other_reservations = Reservation.objects.filter(
                room=self.room, check_out__isnull=True
            ).exists()
            if not has_other_reservations:
                self.room.is_available = 'available'  # Use valid choice
                self.room.save()

    def __str__(self):
        return f"Reservation by {self.client.full_name} for Room {self.room.room_number if self.room else 'N/A'} at {self.hotel.user.username}"

class DailyReservation(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="daily_reservations")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="daily_bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="daily_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.client:
            self.profit = self.client.balance
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_hotel(sender, instance, created, **kwargs):
    if created:
        Hotel.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_hotel(sender, instance, **kwargs):
    if hasattr(instance, "hotel"):
        instance.hotel.save()
