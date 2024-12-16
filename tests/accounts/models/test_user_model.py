from django.test import TestCase
from django.contrib.auth import get_user_model
from kursov_proekt.accounts.models import Profile
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from faker import Faker
fake = Faker()


class CustomBaseUserTest(TestCase):

    def setUp(self):
        # Clean up the database before running tests (to avoid duplicate username errors)
        get_user_model().objects.all().delete()

    def test_user_creation(self):
        """Test that the user is created with valid data."""
        # Create the user explicitly
        user = get_user_model().objects.create_user(
            username="testuser1",
            email="testuser1@example.com",
            password="password123"
        )

        # Assert that the user is created with the correct data
        self.assertEqual(user.username, "testuser1")
        self.assertEqual(user.email, "testuser1@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_username_with_invalid_characters(self):
        with self.assertRaises(ValidationError):
            user = get_user_model()(username="invalid@user")  # Invalid username with '@'
            user.full_clean()  # This triggers the field validations

    def test_username_length_validation(self):
        # Test for a username that is too short (should raise ValidationError)
        short_username = get_user_model()(username="ab")  # Assuming min_length is 3
        with self.assertRaises(ValidationError):
            short_username.full_clean()  # This should raise a ValidationError

        # Test for a username that is too long (should raise ValidationError)
        long_username = get_user_model()(username="a" * 151)  # Assuming max_length is 150
        with self.assertRaises(ValidationError):
            long_username.full_clean()  # This should raise a ValidationError

    def test_username_with_spaces(self):
        # Test for a username with spaces (should raise ValidationError)
        username_with_spaces = get_user_model()(username="test user")  # Contains space
        with self.assertRaises(ValidationError):
            username_with_spaces.full_clean()  # This should raise a ValidationError

    def test_unique_email_and_username(self):
        # Ensure the username is unique
        try:
            # Create the first user
            user1 = get_user_model().objects.create_user(
                username="testuser1",
                email="testuser1@example.com",
                password="password123"
            )

            # Try to create another user with the same username (should raise IntegrityError)
            with self.assertRaises(IntegrityError):
                get_user_model().objects.create_user(
                    username="testuser1",  # Duplicate username
                    email="anotheruser@example.com",
                    password="password456"
                )

        except IntegrityError as e:
            # If we hit the IntegrityError (due to unique username), we pass the test
            self.fail(f"IntegrityError was raised unexpectedly: {str(e)}")


class ProfileTest(TestCase):
    def setUp(self):
        # Create a new user
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
            password="password123"
        )

        # Check if a profile already exists for this user
        if not hasattr(self.user, 'profile'):
            self.profile = Profile.objects.create(
                user=self.user,
                shipping_address_line1="123 Main St",
                city="New York",
                state="NY",
                postal_code="10001",
                country="USA"
            )
        else:
            self.profile = self.user.profile

    def test_profile_creation(self):
        """Test profile creation with shipping address."""
        # Create profile with shipping address line1 set to "123 Main St"
        self.profile.shipping_address_line1 = "123 Main St"
        self.profile.save()

        # Reload the profile to get the latest saved values
        self.profile.refresh_from_db()

        # Check that the shipping_address_line1 is correctly set
        self.assertEqual(self.profile.shipping_address_line1, "123 Main St")

    def test_profile_str_method(self):
        """Test the __str__ method of the Profile model."""
        self.assertEqual(str(self.profile), "testuser's profile")

    def test_optional_fields(self):
        """Test that optional fields can be null or blank."""
        self.profile.phone_number = None
        self.profile.profile_picture = None
        self.profile.size_preferences = None
        self.profile.newsletter_subscribed = True
        self.profile.receive_promotions = False
        self.profile.save()

        self.profile.refresh_from_db()

        # Check that the fields are correctly set to None
        self.assertIsNone(self.profile.phone_number)
        # Instead of assertIsNone, check if the profile picture name is empty
        self.assertEqual(self.profile.profile_picture.name, '')  # Check for empty image
        self.assertIsNone(self.profile.size_preferences)
        self.assertTrue(self.profile.newsletter_subscribed)
        self.assertFalse(self.profile.receive_promotions)
