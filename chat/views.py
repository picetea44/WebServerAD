from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ChatRoom

@login_required
def chat_with(request, user_id):
    other = get_object_or_404(get_user_model(), pk=user_id)
    room = ChatRoom.get_room(request.user, other)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"room_id": room.id, "partner": other.username})
    return redirect("chat:room", room_id=room.id)

@login_required
def latest_room(request):
    room = (
        ChatRoom.objects
        .filter(Q(user1=request.user) | Q(user2=request.user))
        .order_by("-updated_at")          # 최근 활동순
        .select_related("user1", "user2")
        .first()
    )
    if not room:
        return JsonResponse({}, status=204)   # 최근 대화 없음

    partner = room.user2 if room.user1 == request.user else room.user1
    return JsonResponse({"room_id": room.id, "partner": partner.username})

@login_required
def chat_room(request, room_id):
    return render(request, "chat/room.html", {"room_id": room_id})
