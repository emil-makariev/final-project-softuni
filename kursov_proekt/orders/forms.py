from django import forms
from .models import BillingDetails, Orders

class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address',
            'city', 'postal_code', 'country', 'order_notes'
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
            'order_notes': forms.TextInput(attrs={'class': 'checkout__input', 'placeholder': 'Notes about your order, e.g. special notes for delivery.'}),
        }

    def __init__(self, *args, **kwargs):
        order = kwargs.pop('order', None)  # Accept the order keyword argument
        super().__init__(*args, **kwargs)

        # If an order is provided, set it as a hidden value
        if order:
            self.fields['order'] = forms.IntegerField(initial=order.id, widget=forms.HiddenInput())

    def save(self, commit=True):
        billing_details = super().save(commit=False)

        # Ensure the order is assigned correctly
        order_id = self.cleaned_data.get('order')
        if order_id:
            billing_details.order = Orders.objects.get(id=order_id)

        if commit:
            billing_details.save()

        return billing_details
