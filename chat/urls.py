from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("room/<int:room_id>/", views.chat_room, name="room"),
    path("with/<int:user_id>/", views.chat_with, name="with"),
    path("latest/", views.latest_room, name="latest"),
]