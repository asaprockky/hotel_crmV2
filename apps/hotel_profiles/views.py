from django.views.generic import ListView, CreateView, UpdateView, DetailView,View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room, Reservation, DailyReservation
from decimal import Decimal
from django.urls import reverse_lazy
from .models import Reservation, Client, Hotel, TgId, Room
from .forms import ReservationForm , EditReservationForm, getTgId, RoomForm
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




class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'buttons_funcs/reservation_form.html'
    success_url = reverse_lazy('main_page')

    def get_initial(self):
        """Pre-fill the form with the room from the URL."""
        room = self._get_room()
        return {'room': room}

    def get_context_data(self, **kwargs):
        """Add room to the template context."""
        context = super().get_context_data(**kwargs)
        context['room'] = self._get_room()
        return context

    def _get_room(self):
        """Helper method to fetch the room from URL parameter."""
        room_id = self.kwargs.get('room_id')
        return get_object_or_404(Room, id=room_id)

    def send_message_to_boss(self, reservation, profit, days_stayed):
        """Send a Telegram notification to the hotel boss."""
        room = reservation.room
        tgid = TgId.objects.filter(hotel=room.hotel, position='boss').first()
        if tgid and tgid.tg_id:
            message = (
                f"✅ Yangi bandlov!\n"
                f"🏨 Xona raqami: {room.room_number}\n"
                f"📅 Kunlar soni: {days_stayed}\n"
                f"💰 Foyda: ${profit:.2f}\n"
                f"💵 To‘lov (depozit): ${reservation.deposit_amount:.2f}\n"
                f"Rahmat, e'tiboringiz uchun! 😊"
            )
            send_notification(tgid.tg_id, message)

    def form_valid(self, form):
        """Process the form, create reservation, and handle related actions."""
        room = self._get_room()
        if not room.is_available:
            form.add_error(None, 'This room is not available.')
            return self.form_invalid(form)

        # Extract form data
        full_name = form.cleaned_data['full_name']
        passport_number = form.cleaned_data['passport_number']
        deposit = form.cleaned_data['deposit_amount']
        check_in = form.cleaned_data['check_in']
        check_out = form.cleaned_data['check_out']

        # Get or create client for this hotel
        client, created = Client.objects.get_or_create(
            passport_number=passport_number,
            hotel=room.hotel,  # Scope client to this hotel
            defaults={'full_name': full_name, 'balance': Decimal('0.00')}
        )

        # Add deposit to client balance
        client.balance += deposit
        client.save()

        # Calculate stay duration and profit for notification and DailyReservation
        days_stayed = (check_out - check_in).days if check_out else 1
        if days_stayed <= 0:
            form.add_error(None, 'Check-out date must be after check-in date.')
            return self.form_invalid(form)
        profit = room.price * days_stayed

        # Set reservation fields
        form.instance.room = room
        form.instance.hotel = room.hotel
        form.instance.client = client
        form.instance.deposit_amount = deposit
        form.instance.check_in = check_in
        form.instance.check_out = check_out

        # Save the reservation
        response = super().form_valid(form)

        # Create DailyReservation
        DailyReservation.objects.create(
            hotel=room.hotel,
            client=client,
            room=room,
            profit=profit
        )

        # Send notification
        self.send_message_to_boss(form.instance, profit, days_stayed)

        return response

class ReservationEditView(UpdateView):
    model = Reservation
    form_class = EditReservationForm
    template_name = 'buttons_funcs/edit_room_form.html'
    success_url = reverse_lazy('main_page')

    def get_queryset(self):
        """Ensures that users can only edit their own reservations"""
        return Reservation.objects.filter(client=self.request.user)
    
class RoomEditView(LoginRequiredMixin, View):
    template_name = 'buttons_funcs/edit_room.html'

    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id, hotel__user=request.user)
        form = RoomForm(instance=room)
        return render(request, self.template_name, {'form': form, 'room': room})

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id, hotel__user=request.user)
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('main_page')  # Adjust to your room list URL name
        return render(request, self.template_name, {'form': form, 'room': room})
    
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
            room.is_available = "available"

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
    


class RoomListView(LoginRequiredMixin, View):
    template_name = 'buttons_funcs/edit_room_list.html'

    def get(self, request):
        rooms = Room.objects.filter(hotel__user=request.user)
        return render(request, self.template_name, {'rooms': rooms})
# new update for testing