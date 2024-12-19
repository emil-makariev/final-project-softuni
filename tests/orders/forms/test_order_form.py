from django.test import TestCase
from kursov_proekt.accounts.models import CustomBaseUser, Profile
from kursov_proekt.orders.forms import BillingDetailsForm
from kursov_proekt.orders.models import Orders
from django import forms

class BillingDetailsFormTest(TestCase):

    def setUp(self):
        # Cleanup existing data to avoid conflicts
        Profile.objects.all().delete()  # Clear existing Profile instances
        CustomBaseUser.objects.all().delete()  # Clear existing users
        Orders.objects.all().delete()  # Clear existing Orders

        # Create a CustomBaseUser instance
        self.user = CustomBaseUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            first_name='John',
            last_name='Doe',
            password='password123'
        )

        # Check if the user already has a profile, create one if not
        self.profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                'shipping_address_line1': '123 Main St',
                'shipping_address_line2': '',
                'city': 'Test City',
                'state': 'Test State',
                'postal_code': '12345',
                'country': 'Testland',
                'phone_number': '1234567890',
                'profile_picture': None,
                'size_preferences': '',
                'newsletter_subscribed': False,
                'receive_promotions': True
            }
        )

        # Create an Orders instance linked to the Profile
        self.order = Orders.objects.create(
            total_price=100.0,
            discount_codes='SUMMER10',
            profile=self.profile
        )
        print(self.order.id)

        # Valid data for the form
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'address': '123 Main St',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'Testland',
            'account_password': 'password123',
            'order_notes': 'Please deliver after 5 PM',
            'order': self.order.id,  # Make sure to pass the order object
        }

        # Invalid data (for validation checks)
        self.invalid_data = {
            'first_name': '',
            'last_name': '',
            'email': 'invalid-email',
            'phone_number': 'invalid-phone',
            'address': '',
            'city': '',
            'postal_code': '12345',
            'country': 'Testland',
            'account_password': '123',
            'order_notes': 'Please deliver after 5 PM',
            'order': self.order.id,  # Even invalid data needs an order to pass validation
        }

    def test_valid_form_submission(self):
        # Test the form with valid data
        form = BillingDetailsForm(data=self.valid_data)
        self.assertTrue(form.is_valid())  # The form should be valid

    def test_invalid_form_submission(self):
        # Test the form with invalid data (missing first name, invalid email)
        form = BillingDetailsForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())  # The form should not be valid
        self.assertIn('first_name', form.errors)  # Check if the error is for first_name
        self.assertIn('last_name', form.errors)  # Check if the error is for last_name
        self.assertIn('email', form.errors)  # Check if the error is for email

    def test_save_valid_form(self):
        # Pass the order instance into the form constructor
        form = BillingDetailsForm(data=self.valid_data, order=self.order)  # Passing the order instance

        # Ensure the form is valid
        self.assertTrue(form.is_valid())

        # Save the form and get the saved instance
        billing_details = form.save()  # This should now have the order_id

        # Ensure the order_id has been set correctly
        self.assertEqual(billing_details.order.id, self.order.id)

        # Check other fields are saved correctly
        self.assertEqual(billing_details.first_name, 'John')
        self.assertEqual(billing_details.last_name, 'Doe')
        self.assertEqual(billing_details.email, 'john.doe@example.com')
        self.assertEqual(billing_details.order_notes, 'Please deliver after 5 PM')

    def test_password_field(self):
        # Test if the password field is being handled correctly
        form = BillingDetailsForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.fields['account_password'].widget, forms.PasswordInput)
        self.assertEqual(form.fields['account_password'].widget.attrs['placeholder'], 'Account Password')
