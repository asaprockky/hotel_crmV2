from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random


class Hotel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="hotel")
    bio = models.TextField(max_length=500, blank=True)
    date_registered = models.DateField(auto_now_add=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"

class Client(models.Model):
    full_name = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=10, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
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
    check_in = models.DateField()
    check_out = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        
        if self.room:
            self.room.is_available = False
            self.room.save()
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Make the room available only if no other active reservations exist."""
        super().delete(*args, **kwargs)  # Delete the reservation first

        if self.room:
            has_other_reservations = Reservation.objects.filter(
                room=self.room, check_out__isnull=True
            ).exists()

            # Mark the room as available only if there are no active reservations
            if not has_other_reservations:
                self.room.is_available = True
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
