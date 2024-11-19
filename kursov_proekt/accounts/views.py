from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from kursov_proekt.accounts.forms import BaseUserForm, LoginForm


# Create your views here.

class CreateUserView(CreateView):
    template_name = 'user/register.html'
    success_url = reverse_lazy('common')
    model = get_user_model()
    form_class = BaseUserForm

    def form_valid(self, form):
        user = form.save()
        login(request=self.request, user=user)
        return redirect('common')


class LoginViewCustom(LoginView):
    template_name = 'user/log-in.html'
    form_class = LoginForm
    success_url = reverse_lazy('common')

