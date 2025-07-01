from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Hotel, TgId, Room, Plan, Client, Reservation, DailyReservation

# Inline for TgId to manage staff/boss Telegram IDs within Hotel
class TgIdInline(admin.TabularInline):
    model = TgId
    extra = 1
    fields = ('position', 'tg_id')
    verbose_name = "Telegram ID"
    verbose_name_plural = "Telegram IDs"

# Inline for Room to manage rooms within Hotel
class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('room_number', 'room_type', 'price', 'capacity', 'floor', 'air_conditioning', 'is_available')
    verbose_name = "Room"
    verbose_name_plural = "Rooms"

# Inline for Reservation to manage reservations within Hotel or Client
class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 1
    fields = ('client', 'room', 'deposit_amount', 'status', 'check_in', 'check_out', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = "Reservation"
    verbose_name_plural = "Reservations"

# Hotel Admin
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'date_registered', 'balance', 'plan', 'last_payment')
    list_filter = ('plan', 'date_registered')
    search_fields = ('user__username', 'bio')
    inlines = [TgIdInline, RoomInline, ReservationInline]
    fieldsets = (
        (None, {
            'fields': ('user', 'bio')
        }),
        ('Financial Info', {
            'fields': ('balance', 'plan', 'last_payment')
        }),
        ('Metadata', {
            'fields': ('date_registered',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date_registered',)

# Extend UserAdmin to include Hotel inline
class HotelInline(admin.StackedInline):
    model = Hotel
    can_delete = False
    verbose_name_plural = 'Hotel Profile'
    fields = ('bio', 'balance', 'plan', 'last_payment')

class UserAdmin(BaseUserAdmin):
    inlines = (HotelInline,)

# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# TgId Admin
@admin.register(TgId)
class TgIdAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'position', 'tg_id')
    list_filter = ('position',)
    search_fields = ('hotel__user__username', 'tg_id')

# Room Admin
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'room_number', 'room_type', 'price', 'capacity', 'floor', 'air_conditioning', 'is_available')
    list_filter = ('hotel', 'room_type', 'is_available', 'air_conditioning')
    search_fields = ('hotel__user__username', 'room_number', 'room_type')
    list_editable = ('price', 'capacity', 'is_available')
    inlines = [ReservationInline]

# Plan Admin
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'price', 'max_rooms', 'telegram_notifications', 'financial_reports', 'export_excel', 'multi_hotel')
    list_filter = ('key', 'telegram_notifications', 'financial_reports', 'export_excel', 'multi_hotel')
    search_fields = ('name', 'key', 'description')
    fieldsets = (
        (None, {
            'fields': ('key', 'name', 'price', 'description')
        }),
        ('Features', {
            'fields': ('max_rooms', 'telegram_notifications', 'financial_reports', 'export_excel', 'multi_hotel')
        }),
    )

# Client Admin
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'passport_number', 'balance', 'hotel', 'created_at')
    list_filter = ('hotel',)
    search_fields = ('full_name', 'passport_number', 'hotel__user__username')
    inlines = [ReservationInline]
    readonly_fields = ('created_at',)

# Reservation Admin
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'client', 'room', 'deposit_amount', 'status', 'check_in', 'check_out', 'created_at')
    list_filter = ('hotel', 'status', 'check_in', 'check_out')
    search_fields = ('hotel__user__username', 'client__full_name', 'room__room_number')
    readonly_fields = ('created_at',)
    date_hierarchy = 'check_in'

# DailyReservation Admin
@admin.register(DailyReservation)
class DailyReservationAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'client', 'room', 'profit', 'created_at')
    list_filter = ('hotel', 'created_at')
    search_fields = ('hotel__user__username', 'client__full_name', 'room__room_number')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'