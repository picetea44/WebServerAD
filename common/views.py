from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import UserForm, ProfileForm
from .services import UserService
from .exceptions import ValidationException, AuthenticationException, ResourceNotFoundException


class SignupView(View):

    template_name = 'common/signup.html'

    def get(self, request):

        form = UserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):

        form = UserForm(request.POST)
        try:
            if form.is_valid():
                user = UserService.create_user(form)

                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')

                user = UserService.authenticate_user(username, raw_password)
                UserService.login_user(request, user)

                return redirect('index')
        except (ValidationException, AuthenticationException) as e:
            form.add_error(None, str(e))

        return render(request, self.template_name, {'form': form})


def signup(request):

    view = SignupView.as_view()
    return view(request)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class ProfileView(View):

    template_name = 'common/profile.html'

    def get(self, request, user_id=None):

        if user_id is None:
            user_id = request.user.id

        try:
            profile = UserService.get_user_profile(user_id)
            return render(request, self.template_name, {'profile': profile})
        except ResourceNotFoundException:
            return get_object_or_404(User, pk=user_id)


@method_decorator(login_required(login_url='common:login'), name='dispatch')
class ProfileUpdateView(View):

    template_name = 'common/profile_form.html'

    def get(self, request):

        try:
            profile = UserService.get_user_profile(request.user.id)
            form = ProfileForm(instance=profile)
            return render(request, self.template_name, {'form': form})
        except ResourceNotFoundException:
            # If profile is not found, return 404
            return get_object_or_404(User, pk=request.user.id)

    def post(self, request):

        try:
            profile = UserService.get_user_profile(request.user.id)
            form = ProfileForm(request.POST, request.FILES, instance=profile)

            try:
                if form.is_valid():
                    UserService.update_profile(form)
                    messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
                    return redirect('common:profile')
            except ValidationException as e:
                form.add_error(None, str(e))

            return render(request, self.template_name, {'form': form})
        except ResourceNotFoundException:
            return get_object_or_404(User, pk=request.user.id)


# For backwards compatibility
@login_required(login_url='common:login')
def profile(request, user_id=None):

    view = ProfileView.as_view()
    return view(request, user_id=user_id)


@login_required(login_url='common:login')
def profile_update(request):
    view = ProfileUpdateView.as_view()
    return view(request)
