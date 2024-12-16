from django.test import TestCase
from django import forms
from django.contrib.auth import get_user_model
from kursov_proekt.accounts.forms import BaseUserForm, LoginForm
from django.contrib.auth.forms import AuthenticationForm

class BaseUserFormTestCase(TestCase):
    def test_valid_form(self):
        """Test valid data for BaseUserForm."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john.doe@example.com',
            'password1': 'StrongerPassword123!',  # Updated password
            'password2': 'StrongerPassword123!',  # Make sure both passwords match
        }
        form = BaseUserForm(data)

        # Print form errors to diagnose why it's invalid
        if not form.is_valid():
            print(form.errors)  # This will show why the form isn't valid

        self.assertTrue(form.is_valid())  # T

    def test_invalid_form(self):
        """Test invalid data for BaseUserForm (passwords do not match)."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john.doe@example.com',
            'password1': 'password123',
            'password2': 'differentpassword123',
        }
        form = BaseUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  # Passwords do not match error

    def test_missing_required_fields(self):
        """Test required fields in BaseUserForm."""
        data = {
            'first_name': '',
            'last_name': '',
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
        }
        form = BaseUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 6)  # All fields are required

    def test_field_widgets(self):
        """Test that the form fields use the correct widgets."""
        form = BaseUserForm()
        self.assertIn('class="form-control"', str(form['first_name']))
        self.assertIn('class="form-control"', str(form['last_name']))
        self.assertIn('class="form-control"', str(form['username']))
        self.assertIn('class="form-control"', str(form['email']))
        self.assertIn('class="form-control"', str(form['password1']))
        self.assertIn('class="form-control"', str(form['password2']))


class LoginFormTestCase(TestCase):
    def test_valid_form(self):
        """Test valid data for LoginForm."""
        user = get_user_model().objects.create_user(
            username='johndoe', password='password123', email='john.doe@example.com')
        data = {
            'username': 'johndoe',
            'password': 'password123'
        }
        form = LoginForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """Test invalid data for LoginForm (wrong password)."""
        user = get_user_model().objects.create_user(
            username='johndoe', password='password123', email='john.doe@example.com')
        data = {
            'username': 'johndoe',
            'password': 'wrongpassword'
        }
        form = LoginForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  # Invalid password error

    def test_missing_required_fields(self):
        """Test required fields in LoginForm."""
        data = {
            'username': '',
            'password': '',
        }
        form = LoginForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Both fields are required

    def test_field_widgets(self):
        """Test that the form fields use the correct widgets."""
        form = LoginForm()
        self.assertIn('class="form-control"', str(form['username']))
        self.assertIn('class="form-control"', str(form['password']))

