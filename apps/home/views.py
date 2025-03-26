from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, RoomForm
from apps.hotel_profiles.models import Room
from django.contrib.auth.mixins import LoginRequiredMixin

class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'main_page.html'
    login_url = reverse_lazy('login')


class SignUpview(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('main_page')
    template_name = 'common/register.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'settings.html'
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
