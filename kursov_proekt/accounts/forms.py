from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.utils.translation import gettext_lazy as _

from kursov_proekt.accounts.models import CustomBaseUser, Profile


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

class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            'shipping_address_line1',
            'shipping_address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'phone_number',
            'profile_picture',
            'size_preferences',
            'newsletter_subscribed',
            'receive_promotions',
            'description',
        ]

    # Customizing the widgets for each field
    shipping_address_line1 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_address_line2 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    postal_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_picture = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    size_preferences = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    newsletter_subscribed = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False
    )
    receive_promotions = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        initial="There is no description"
    )
