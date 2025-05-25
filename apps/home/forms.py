from django import forms
from django.contrib.auth.models import User
from apps.hotel_profiles.models import Room
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length= 30, required= False, help_text= 'optional')
    class Meta:
        

        
        model = User
        fields = [
        "first_name",
        "username",
        "password1",
        "password2"
    ]

