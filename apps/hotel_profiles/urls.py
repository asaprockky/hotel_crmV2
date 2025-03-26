from django.urls import path
from .views import ShowRoomsView  # Import the view

urlpatterns = [
    path('rooms/', ShowRoomsView.as_view(), name='room_list'),  # URL pattern
]
