from django import forms
from .models import BillingDetails

class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address',
            'city', 'postal_code', 'country', 'account_password'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'checkout__input', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'Phone'}),
            'address': forms.TextInput(attrs={'class': 'checkout__input checkout__input__add', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'Town/City'}),
            'postal_code': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'Postcode/ZIP'}),
            'country': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'Country'}),
            'account_password': forms.PasswordInput(attrs={'class': 'checkout__input', 'placeholder': 'Account Password'}),
            'order_note': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'Notes about your order, e.g. special notes for delivery.'}),

        }