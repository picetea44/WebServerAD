
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .exceptions import ValidationException, AuthenticationException, ResourceNotFoundException
from .models import Profile


class UserService:

    @staticmethod
    def create_user(form_data):

        if not form_data.is_valid():
            raise ValidationException("Invalid user data")

        # Save the user
        user = form_data.save()
        return user

    @staticmethod
    def authenticate_user(username, password):

        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationException("Invalid username or password")
        return user

    @staticmethod
    def login_user(request, user):

        login(request, user)

    @staticmethod
    def get_user_profile(user_id):

        try:
            user = User.objects.get(pk=user_id)
            return user.profile
        except User.DoesNotExist:
            raise ResourceNotFoundException(f"User with ID {user_id} not found")

    @staticmethod
    def update_profile(profile_form):

        if not profile_form.is_valid():
            raise ValidationException("Invalid profile data")

        # Save the profile
        profile = profile_form.save()
        return profile
