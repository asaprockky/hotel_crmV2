from django.views.generic import ListView, CreateView, UpdateView, DetailView,View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room, Reservation, DailyReservation
from decimal import Decimal
from django.urls import reverse, reverse_lazy
from .models import Reservation, Client, Hotel, TgId, Room, Plan
from .forms import ReservationForm , EditReservationForm, getTgId, RoomForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from datetime import timedelta, date, datetime
from django.db import transaction
from django.db.models import Sum, Avg, F ,Q
from django.http import HttpResponseForbidden
from django.views.generic.edit import FormView
from .bot import send_notification
import json
from django.core.exceptions import ValidationError
from django.http import JsonResponse
class ShowRoomsView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'common/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = super().get_queryset().filter(hotel=self.request.user.hotel)
        
        # Get filter parameters from GET request
        room_type = self.request.GET.get('room_type')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        capacity = self.request.GET.get('capacity')
        air_conditioning = self.request.GET.get('air_conditioning')
        room_number = self.request.GET.get('room_number')
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        
        # Apply filters
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if capacity:
            queryset = queryset.filter(capacity__gte=capacity)
        if air_conditioning:
            queryset = queryset.filter(air_conditioning=True)
        if room_number:
            queryset = queryset.filter(room_number__icontains=room_number)
        
        # Date range filtering (check for reservations in this period)
        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                
                # Get rooms that have conflicting reservations
                reserved_rooms = Reservation.objects.filter(
                    Q(check_in__lt=check_out_date) & Q(check_out__gt=check_in_date)
                ).values_list('room_id', flat=True)
                
                # Exclude reserved rooms
                queryset = queryset.exclude(id__in=reserved_rooms)
            except ValueError:
                pass
        
        return queryset
    
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
    
    def get_reserved_dates(self):
        room = self._get_room()
        today = timezone.now().date()
        reservations = Reservation.objects.filter(room = room, check_out__gte = today).values_list('check_in', 'check_out')
        reserved = set()
        for check_in, check_out in reservations:
            # loop over the span of each booking (inclusive of check_out)
            for n in range((check_out - check_in).days + 1):
                reserved.add((check_in + timedelta(days=n)).isoformat())

        return sorted(reserved)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = self._get_room()
        context['reserved_dates'] = self.get_reserved_dates()
        return context


    def _get_room(self):
        """Helper method to fetch the room from URL parameter."""
        room_id = self.kwargs.get('room_id')
        return get_object_or_404(Room, id=room_id)

    def send_message_to_boss(self, reservation, profit, days_stayed):
        """Send a Telegram notification to the hotel boss."""
        room = reservation.room
        hotel = room.hotel
        if hotel.plan == "basic":
            return
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
        conflicting_reservations =  Reservation.objects.filter(room_id = room.id, check_in__lte = check_out, check_out__gte=check_in)
        if conflicting_reservations.exists():
            form.add_error(None, 'Xona Ushbu sanalarda mavjud emas')
            return self.form_invalid(form)
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

class EditReservationView(View):
    template_name = 'buttons_funcs/edit_reservation_form.html'

    def get(self, request, *args, **kwargs):
        reservation_id = kwargs['pk']
        reservation = get_object_or_404(Reservation, id=reservation_id, room__hotel=request.user.hotel)
        initial_data = {
            'check_in': reservation.check_in,
            'check_out': reservation.check_out,
            'room': reservation.room,
            'deposit_amount': reservation.deposit_amount,
        }
        form = EditReservationForm(instance=reservation, initial=initial_data)
        print(f"Form Initial Data: {form.initial}")
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        reservation_id = kwargs['pk']
        reservation = get_object_or_404(Reservation, id=reservation_id, room__hotel=request.user.hotel)
        form = EditReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('reservation_detail', pk=reservation.pk)
        return render(request, self.template_name, {'form': form})
    
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
from django.utils import timezone
class ShowReservedRoomView(ListView):
    model = Reservation
    template_name = 'pages/edit_room_page.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        today = now().date()
        return Reservation.objects.filter(room_id = room_id, check_out__gte=today)
    
    

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
                'passport': res.client.passport_number, 
                'has_to_pay' : ((res.check_out - res.check_in).days) * res.room.price - res.client.balance if res.check_out else 1 * res.room.price - res.client.balance
            }
            for res in reservations
        ]
        context['room'] = room
        
        return context

class EditReservationView(UpdateView):
    model = Reservation
    form_class = EditReservationForm
    template_name = 'buttons_funcs/edit_reservation_form.html'
    context_object_name = 'reservation'

    def get_queryset(self):
        # Optional: limit access to reservations related to user's hotel
        return Reservation.objects.filter(room__hotel=self.request.user.hotel)

    def get_success_url(self):
        # Redirect after successful update
        return reverse('reservation_detail', kwargs={'pk': self.object.pk})

class CloseRoomCommand(View):
    model = Reservation
    def send_message_to_boss(self, reservation,profit, days_stayed):
        """Send a Telegram notification to the hotel staff."""
        room = reservation.room
        tgid = TgId.objects.filter(hotel=room.hotel, position='staff').first()
        hotel = room.hotel
        if hotel.plan == "basic":
            return
        if tgid and tgid.tg_id:
            message = (
                f"✅ Xona yopildi!\n"
                f"🏨 Xona raqami: {room.room_number}\n"
                f"📅 Kunlar soni: {days_stayed}\n"
                f"Iltimos xonani tozalang"
                f"Rahmat, e'tiboringiz uchun! 😊"
            )
            print(tgid)
            send_notification(tgid.tg_id, message)    
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
            days_stayed = (reservation.check_out - reservation.check_in).days

            # Save daily reservation
            DailyReservation.objects.create(
                hotel=user.hotel,
                client=client,
                room=room,
                profit=client.balance  # Save profit before resetting balance
            )

            client.balance = 0
            

            reservation.save()
            client.save()
            
            room_id = reservation.room_id
            Reservation.objects.filter(id = reservation.id).delete()
            res = Reservation.objects.filter(room_id =room_id ).first()
            if res:
                status = res.status
                room.is_available = status.lower()
                print(status)
                room.save()
            else:
                print(f'{room.room_number} is changing')
                room.is_available = "available"
                room.save()

        profit = client.balance
        self.send_message_to_boss(reservation,profit, days_stayed)
        print("Room closed successfully.")

        return render(request, 'details/close_room_success.html', {'room': room})



        
class StatsView(LoginRequiredMixin, View):
    def get(self, request):
        # Ensure user is authenticated and has a linked hotel
        if not hasattr(request.user, 'hotel'):
            return render(request, 'stats.html', {'error': "Mehmonxona topilmadi"})

        hotel = request.user.hotel
        today = timezone.localdate()

        # Room Statistics
        total_rooms = Room.objects.filter(hotel=hotel).count()
        available_rooms = Room.objects.filter(hotel=hotel, is_available='available').count()
        unavailable_rooms = Room.objects.filter(hotel=hotel, is_available='unavailable').count()
        reserved_rooms = Room.objects.filter(hotel=hotel, is_available='reserved').count()

        # Revenue Statistics (handling Decimal)
        total_revenue = DailyReservation.objects.filter(hotel=hotel).aggregate(Sum('profit'))['profit__sum'] or 0
        total_revenue = float(total_revenue) if total_revenue else 0.0

        revenue_today = DailyReservation.objects.filter(hotel=hotel, created_at__date=today).aggregate(Sum('profit'))['profit__sum'] or 0
        revenue_today = float(revenue_today) if revenue_today else 0.0

        start_of_week = today - timedelta(days=today.weekday())
        revenue_week = DailyReservation.objects.filter(hotel=hotel, created_at__date__gte=start_of_week).aggregate(Sum('profit'))['profit__sum'] or 0
        revenue_week = float(revenue_week) if revenue_week else 0.0

        start_of_month = today.replace(day=1)
        revenue_month = DailyReservation.objects.filter(hotel=hotel, created_at__date__gte=start_of_month).aggregate(Sum('profit'))['profit__sum'] or 0
        revenue_month = float(revenue_month) if revenue_month else 0.0

        # Occupancy Rate
        occupancy_rate = ((unavailable_rooms + reserved_rooms) / total_rooms * 100) if total_rooms > 0 else 0
        occupancy_rate = round(float(occupancy_rate), 2)

        # Average Stay Duration
        average_stay = Reservation.objects.filter(hotel=hotel, check_out__isnull=False).annotate(
            stay_duration=F('check_out') - F('check_in')
        ).aggregate(Avg('stay_duration'))['stay_duration__avg']
        average_stay_days = int(average_stay.days) if average_stay else 0

        # Client Statistics
        total_clients = Client.objects.filter(hotel=hotel).count()
        new_clients_today = Client.objects.filter(hotel=hotel, created_at__date=today).count()
        new_clients_week = Client.objects.filter(hotel=hotel, created_at__date__gte=start_of_week).count()
        new_clients_month = Client.objects.filter(hotel=hotel, created_at__date__gte=start_of_month).count()

        # Chart Data
        # Room Status Pie Chart
        room_status_labels = ['Bo\'sh', 'Band', 'Rezervlangan']
        room_status_data = [available_rooms, unavailable_rooms, reserved_rooms]

        # Revenue Line Chart (last 7 days)
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        revenue_data = [
            float(DailyReservation.objects.filter(hotel=hotel, created_at__date=date).aggregate(Sum('profit'))['profit__sum'] or 0)
            for date in dates
        ]
        date_labels = [date.strftime('%d-%m-%Y') for date in dates]

        # New Clients Bar Chart (last 7 days)
        new_clients_data = [
            Client.objects.filter(hotel=hotel, created_at__date=date).count()
            for date in dates
        ]

        # Prepare context
        context = {
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'unavailable_rooms': unavailable_rooms,
            'reserved_rooms': reserved_rooms,
            'total_revenue': total_revenue,
            'revenue_today': revenue_today,
            'revenue_week': revenue_week,
            'revenue_month': revenue_month,
            'occupancy_rate': occupancy_rate,
            'average_stay_days': average_stay_days,
            'total_clients': total_clients,
            'new_clients_today': new_clients_today,
            'new_clients_week': new_clients_week,
            'new_clients_month': new_clients_month,
            'room_status_labels': json.dumps(room_status_labels),  # Safe: strings
            'room_status_data': json.dumps(room_status_data),  # Safe: integers
            'date_labels': json.dumps(date_labels),  # Safe: strings
            'revenue_data': json.dumps(revenue_data),  # Safe: floats
            'new_clients_data': json.dumps(new_clients_data),  # Safe: integers
        }

        return render(request, 'pages/stats.html', context)
    

class AddTgFormView(FormView):
    template_name = "buttons_funcs/add_tg.html"
    form_class = getTgId  
    success_url = '/main/'  

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




class PaymentView(LoginRequiredMixin, View):
    template_name = 'pages/payment.html'
    def get(self, request):
        hotel = request.user.hotel
        balance = hotel.balance
        print(balance)
        plan = hotel.plan
        if hotel.last_payment:
            next_payment_date = hotel.last_payment + timedelta(days= 31)
        else:
            next_payment_date = "To'lov mavjud emas"
        context = {
            'balance' : balance,
            'plan': plan, 
            "next_payment_date" : next_payment_date
        }
        return render(request, self.template_name, context)
    def post(self, request):
        data = json.loads(request.body)
        plan = data.get('plan')
        print(plan)
        hotel = request.user.hotel
        cplan = Plan.objects.get(key= plan)
        if hotel.balance >= cplan.price:
            hotel.plan = plan.lower()
            hotel.balance = hotel.balance - cplan.price
            now = timezone.now()
            hotel.last_payment = now
            hotel.save()
            return JsonResponse({'success': True, 'plan': cplan.name})
        else:
            print('wewew')
            return JsonResponse({'error' : 'Balansda yetarli mablag mavjud emas'}, status = 400)