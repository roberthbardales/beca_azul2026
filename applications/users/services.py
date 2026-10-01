from django.contrib.auth import authenticate, login, logout

from .models import User


def authenticate_user(request, email, password):
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
    return user


def change_password(user, new_password):
    user.set_password(new_password)
    user.save(update_fields=['password'])


def logout_user(request):
    logout(request)
