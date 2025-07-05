from django import forms
from .models import Reservation, Client, Room, TgId

class ReservationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        label="Client Name"
    )
    passport_number = forms.CharField(
        max_length=10,
        required=True,
        label="Passport Number"
    )
    deposit_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        label="Deposit Amount"
    )

    class Meta:
        model = Reservation
        fields = ['deposit_amount', 'check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        if check_in and check_out and check_out <= check_in:
            self.add_error('check_out', 'Check-out date must be after check-in date.')
        return cleaned_data

    def save(self, commit=True):
        """Save the reservation instance."""
        reservation = super().save(commit=False)
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


class getTgId(forms.ModelForm):
    class Meta:
        model = TgId
        fields = ['tg_id', 'position']

class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price', 'is_available', 'capacity']
        widgets = {
            'room_type' : forms.TextInput(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'is_available': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_room_number(self):
        room_number = self.cleaned_data['room_number']
        if len(str(room_number)) > 6:
            raise forms.ValidationError("Room number cannot exceed 6 characters.")
        return room_number

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price
    

class EditReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['check_in', 'check_out', 'room', 'deposit_amount']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }