from django.views.generic import ListView, CreateView, UpdateView, DetailView,View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room, Reservation, DailyReservation
from django.urls import reverse_lazy
from .models import Reservation, Client, Hotel, TgId
from .forms import ReservationForm , EditReservationForm, getTgId
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from datetime import timedelta, date
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.views.generic.edit import FormView
from .bot import send_notification


class ShowRoomsView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'common/room_list.html'  # Ensure this file exists
    context_object_name = 'rooms'  # This is how rooms will be accessed in the template

    def get_queryset(self):
        """Filter rooms based on the logged-in user's hotel"""
        hotel = self.request.user.hotel  # Assuming a user owns one hotel
        return Room.objects.filter(hotel=hotel)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_rooms'] = range(6)  # Ensuring the template gets range(6)
        return context
    
class ShowReservedRooms(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'common/reservations_list.html'  # Ensure this file exists
    context_object_name = 'rooms'  # This is how rooms will be accessed in the template

    def get_queryset(self):
        """Filter rooms based on the logged-in user's hotel"""
        hotel = self.request.user.hotel  # Assuming a user owns one hotel
        return Room.objects.filter(hotel=hotel)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_rooms'] = range(6)  # Ensuring the template gets range(6)
        return context
    def post(self, request, *args, **kwargs):
        room = self.get_object()  # Get the room object
        room.is_available = True
        room.save()
        return redirect('some_success_url') 




class ReservationCreateView(CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'buttons_funcs/reservation_form.html'
    success_url = reverse_lazy('main_page')

    def get_initial(self):
        """Pre-fill the form with the room ID from the URL."""
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        return {'room': room}

    def get_context_data(self, **kwargs):
        """Pass room to the template explicitly."""
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs.get('room_id')
        context['room'] = get_object_or_404(Room, id=room_id)
        return context
    
    def send_message_to_boss(self, form):
        tgid = TgId.objects.filter(hotel__user=self.request.user, position='boss').first()
        print(tgid)
        if tgid and tgid.tg_id:
            balance = form.cleaned_data.get('balance')
            room_id = self.kwargs.get('room_id')
            room = get_object_or_404(Room, id=room_id)
            mssg = f"""
            🎉 To'ldirish
            📍 Xona Raqami {room}.
            ➕ {balance} $
            Thank you for your attention! 😊
            """
            send_notification(tgid.tg_id, mssg)

        
    def form_valid(self, form):
        """Assign the room, hotel, and client to the reservation."""
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)

        form.instance.room = room  # Assign the room
        form.instance.hotel = room.hotel  # Assign the hotel

        # Get client details from the form
        full_name = form.cleaned_data.get('full_name')
        passport_number = form.cleaned_data.get('passport_number')
        balance = form.cleaned_data.get('balance')

        # Create or get the client
        client, created = Client.objects.get_or_create(
            passport_number=passport_number,
            defaults={'full_name': full_name, 'balance': balance}
        )

        form.instance.client = client  # Assign the client to the reservation
    def form_valid(self, form):
        """Assign the room, hotel, and client to the reservation."""
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, id=room_id)

        form.instance.room = room  # Assign the room
        form.instance.hotel = room.hotel  # Assign the hotel

        # Get client details from the form
        full_name = form.cleaned_data.get('full_name')
        passport_number = form.cleaned_data.get('passport_number')
        balance = form.cleaned_data.get('balance')

        # Create or get the client
        client, created = Client.objects.get_or_create(
            passport_number=passport_number,
            defaults={'full_name': full_name, 'balance': balance}
        )

        form.instance.client = client  # Assign the client to the reservation

        # Save the reservation
        response = super().form_valid(form)
        DailyReservation.objects.create(
            hotel=room.hotel,
            client=client,
            room=room,
            profit=client.balance  # Store the client's balance at the time of creation
        )
        self.send_message_to_boss(form)
        return super().form_valid(form)


class ReservationEditView(UpdateView):
    model = Reservation
    form_class = EditReservationForm
    template_name = 'buttons_funcs/edit_room_form.html'
    success_url = reverse_lazy('main_page')

    def get_queryset(self):
        """Ensures that users can only edit their own reservations"""
        return Reservation.objects.filter(client=self.request.user)
    

class ShowReservedRoomView(ListView):
    model = Reservation
    template_name = 'pages/edit_room_page.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return Reservation.objects.filter(room_id = room_id)
    
    

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        reservations = self.get_queryset()
        room = reservations.first().room if reservations.exists() else None  
        context['reservation_data'] = [
            {
                'reservation': res,
                'client': res.client,
                'room': res.room,
                'check_in': res.check_in,
                'check_out': res.check_out,
                'balance': res.client.balance,
                'passport': res.client.passport_number,  # Assuming client model has this field
            }
            for res in reservations
        ]
        context['room'] = room
        
        return context

class CloseRoomCommand(View):
    model = Reservation
    
    def post(self, request, *args, **kwargs):
        room_id = self.kwargs['pk']
        user = request.user
        room = get_object_or_404(Room, id=room_id, hotel=user.hotel)

        reservation = Reservation.objects.filter(room=room).order_by('-created_at').first()

        if not reservation:
            print("No active reservation found for this room.")
            return render(request, 'details/close_room_error.html', {'room': room})

        client = reservation.client

        with transaction.atomic():
            reservation.check_out = now().date()

            # Save daily reservation
            DailyReservation.objects.create(
                hotel=user.hotel,
                client=client,
                room=room,
                profit=client.balance  # Save profit before resetting balance
            )

            client.balance = 0
            room.is_available = True

            reservation.save()
            client.save()
            room.save()
        
        print("Room closed successfully.")
        return render(request, 'details/close_room_success.html', {'room': room})


PASSCODE = '1234'

class EnterPasscodeView(TemplateView):
    template_name = "details/enter_pass.html"

class VerifyPasscodeView(View):
    def post(self, request, *args, **kwargs):
        entered_passcode = request.POST.get('passcode')

        if entered_passcode == PASSCODE:
            # Store passcode validation state in session for this session
            request.session['is_passcode_valid'] = True
            request.session.set_expiry(200)
            return redirect('stats')  # Redirect to stats page after correct passcode
        else:
            return HttpResponseForbidden("Incorrect passcode. Please try again.")
        
class StatsView(TemplateView):
    template_name = "pages/stats.html"

    def dispatch(self, request, *args, **kwargs):
        # Check if the passcode is validated in the session
        if not request.session.get('is_passcode_valid', False):
            return redirect('enter_passcode')  # Redirect to passcode entry if not validated
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ensure the logged-in user has a hotel
        try:
            hotel = Hotel.objects.get(user=self.request.user)
        except Hotel.DoesNotExist:
            hotel = None
        
        one_week_ago = now() - timedelta(days=7)
        if hotel:
            # Gathering statistics
            total_clients = Client.objects.filter(reservations__hotel=hotel).distinct().count()
            available_rooms = Room.objects.filter(hotel=hotel, is_available=True).count()
            total_rooms = Room.objects.filter(hotel=hotel).count()
            active_reservations = Reservation.objects.filter(hotel=hotel, check_out__isnull=True).count()
            total_revenue = DailyReservation.objects.filter(hotel=hotel).aggregate(Sum('profit'))['profit__sum'] or 0
            daily_profit = DailyReservation.objects.filter(hotel=hotel, created_at__date=date.today()).aggregate(Sum('profit'))['profit__sum'] or 0
            recent_reservations = Reservation.objects.filter(hotel=hotel).order_by('-created_at')[:5]
            new_clients_week = Client.objects.filter(created_at__gte=one_week_ago).count()
            occupancy_rate = (Reservation.objects.filter(hotel=hotel).count() / total_rooms) * 100 if total_rooms > 0 else 0
            ending_soon = Reservation.objects.filter(hotel=hotel, check_out__lte=date.today()+timedelta(days=3)).count()
        else:
            # Default values if the user has no hotel
            total_clients = available_rooms = total_rooms = active_reservations = total_revenue = daily_profit = 0
            recent_reservations = []
            occupancy_rate = ending_soon = 0
        
        # Adding data to context
        context.update({
            'hotel': hotel,
            'total_clients': total_clients,
            'available_rooms': available_rooms,
            'total_rooms': total_rooms,
            'active_reservations': active_reservations,
            'total_revenue': total_revenue,
            'daily_profit': daily_profit,
            'recent_reservations': recent_reservations,
            'occupancy_rate': occupancy_rate,
            'new_clients_week': new_clients_week,
            'ending_soon': ending_soon,
        })
        
        return context
    

class AddTgFormView(FormView):
    template_name = "buttons_funcs/add_tg.html"
    form_class = getTgId  
    success_url = '/main_page/'  

    def form_valid(self, form):
        tg_id_instance = form.save(commit=False)
        tg_id_instance.hotel = self.request.user.hotel
        tg_id_instance.save()
        return super().form_valid(form) 