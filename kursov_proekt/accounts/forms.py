from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.utils.translation import gettext_lazy as _

from kursov_proekt.accounts.models import CustomBaseUser

class BaseUserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name','last_name', 'username', 'email', 'password1', 'password2']

    first_name = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
            widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True, 'class': 'form-control',
                                                          }))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", 'class': 'form-control',
                                         }),
    )

