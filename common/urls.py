from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import SignupView, ProfileView, ProfileUpdateView

app_name = 'common'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile_user'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
]
