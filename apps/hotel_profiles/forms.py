from django import forms
from .models import Reservation, Client, Room

class ReservationForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, required=True, label="Client Name")
    passport_number = forms.CharField(max_length=10, required=True, label="Passport Number")
    balance = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label="Client Balance")

    class Meta:
        model = Reservation
        fields = ['full_name', 'passport_number', 'balance', 'check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


    def save(self, commit=True):
        """Create or update the client and link it to the reservation"""
        full_name = self.cleaned_data.get('full_name')
        passport_number = self.cleaned_data.get('passport_number')
        balance = self.cleaned_data.get('balance')

        client_id, created = Client.objects.get_or_create(
            passport_number=passport_number,
            defaults={'full_name': full_name, 'balance': balance},
        )

        reservation = super().save(commit=False)
        reservation.client_id = client_id  # Link the reservation to the client

        if commit:
            reservation.save()

        return reservation
    

class EditReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['check_out' ]
        widgets = {
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }