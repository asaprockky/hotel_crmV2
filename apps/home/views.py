from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm
from apps.hotel_profiles.forms import RoomForm
from apps.hotel_profiles.models import Room, Hotel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/main_page.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = self.request.user.hotel

        total_rooms = Room.objects.filter(hotel=hotel).count()
        available_rooms = Room.objects.filter(hotel=hotel, is_available="available").count()
        unavailable_rooms = Room.objects.filter(hotel=hotel, is_available="unavailable").count()
        reserved_rooms = Room.objects.filter(hotel=hotel, is_available="reserved").count()

        # Avoid division by zero
        if total_rooms > 0:
            percent_available = int(round((available_rooms / total_rooms) * 100))
            percent_unavailable = int(round((unavailable_rooms / total_rooms) * 100))
            percent_reserved = int(round((reserved_rooms / total_rooms) * 100))
        else:
            percent_available = percent_unavailable = percent_reserved = 0

        context.update({
            'percent_available': percent_available,
            'percent_unavailable': percent_unavailable,
            'percent_reserved': percent_reserved,
            'total_rooms': total_rooms,
        })

        return context


class SignUpview(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('main_page')
    template_name = 'common/register.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/settings.html'
    login_url = reverse_lazy('settings')


class RegisterRoomView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'buttons_funcs/add_room.html'
    success_url = reverse_lazy('main_page')

    def form_valid(self, form):
        """Assign the logged-in user's hotel to the room before saving"""
        room = form.save(commit=False)
        room.hotel = self.request.user.hotel  # Assign hotel to the room
        room.save()
        return super().form_valid(form)
    

