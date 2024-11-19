from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import CreateView

from kursov_proekt.accounts.forms import BaseUserForm


# Create your views here.

class CreateUserView(CreateView):
    template_name = 'user/register.html'
    success_url = 'home'
    model = get_user_model()
    form_class = BaseUserForm


class LoginViewCustom(LoginView):
    pass
