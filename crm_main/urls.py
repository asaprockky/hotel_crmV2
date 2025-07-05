"""
URL configuration for crm_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
from django.conf import settings
from django.views.static import serve
import apps
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from apps.home.views import SignUpview, MainPageView, SettingsView, RegisterRoomView
from apps.hotel_profiles.views import ShowRoomsView,RoomListView, PaymentView, EditReservationView, ReservationCreateView, ShowReservedRoomView, ShowReservedRooms,RoomEditView, CloseRoomCommand,AddTgFormView, StatsView, EnterPasscodeView, VerifyPasscodeView
from django.contrib.auth import views as auth_views
APPEND_SLASH = True
urlpatterns = [
    path('admin/', admin.site.urls),
    path('mobile/', include('apps.mobile.urls')),
    path("", MainPageView.as_view(), name="main_page"),
    path("main/", MainPageView.as_view(), name="main_page"),
    path('register/', SignUpview.as_view(), name = 'register' ),
    path('login/', auth_views.LoginView.as_view(template_name = 'common/login.html'), name = "login" ),
    path('logout/', auth_views.LogoutView.as_view(next_page = 'login'), name = "logout" ),
    path('settings/', SettingsView.as_view(template_name = 'pages/settings.html'), name = "settings" ),
    path('add_room/', RegisterRoomView.as_view(), name = 'add_room' ),
    path('room_list/', ShowRoomsView.as_view(template_name = 'common/room_list.html'), name = 'room_list' ),
    path('reserve/<int:room_id>/', ReservationCreateView.as_view(), name='reserve_room'),
    path('close_room_list/', ShowReservedRooms.as_view(template_name = 'common/reservations_list.html'), name = 'close_rooms_list' ),
    path('edit_reserve/<int:room_id>/', ShowReservedRoomView.as_view(), name='edit_reserved_room'),
    path('reservation/<int:pk>/', EditReservationView.as_view(), name='edit_reservation'),
    path('close_room/<int:pk>/', CloseRoomCommand.as_view(), name='close_room'),
    path('enter-passcode/', EnterPasscodeView.as_view(), name='enter_passcode'),
    path('verify-passcode/', VerifyPasscodeView.as_view(), name='verify_passcode'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('add_tg/', AddTgFormView.as_view(), name= "add_tg" ),
    path('rooms/<int:room_id>/edit/', RoomEditView.as_view(), name='edit_room'),
    path('rooms/', RoomListView.as_view(), name='edit_room_list'),
    path('payment/', PaymentView.as_view(), name='payment'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]