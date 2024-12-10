from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from kursov_proekt.accounts.manager import CustomUserManager
from kursov_proekt.accounts.validators.username_validation import UserNameValidatorTyping, UserNameLengthValidator, \
    UsernameContainsNoSpacesValidator


class CustomBaseUser(AbstractBaseUser, PermissionsMixin):
    MAX_LENGTH = 20
    MIN_LENGTH = 3

    username = models.CharField(
        unique=True,
        null=False,
        blank=False,
        validators=(
            UserNameValidatorTyping(),
            UserNameLengthValidator(MIN_LENGTH, MAX_LENGTH),
            UsernameContainsNoSpacesValidator()
        )
    )

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False
    )
    first_name = models.CharField(
        null=False,
        blank=False,
        max_length=MAX_LENGTH,
        validators=(
            MinLengthValidator(MIN_LENGTH),
        )
    )
    last_name = models.CharField(
        null=False,
        blank=False,
        max_length=MAX_LENGTH,
        validators=(
            MinLengthValidator(MIN_LENGTH),
        )
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        )
    )
    site_staff_member = models.BooleanField(
        default=False
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()


class Profile(models.Model):
    user = models.OneToOneField(
        to=CustomBaseUser,
        on_delete=models.CASCADE,
        primary_key=True
    )
    # Shipping Address
    shipping_address_line1 = models.CharField(
        max_length=255
    )
    shipping_address_line2 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    city = models.CharField(
        max_length=100
    )
    state = models.CharField(
        max_length=100
    )
    postal_code = models.CharField(
        max_length=20
    )
    country = models.CharField(
        max_length=100
    )

    # Other profile information
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    profile_picture = models.ImageField(
        upload_to='mediafiles/',
        blank=True,
        null=True
    )
    size_preferences = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    newsletter_subscribed = models.BooleanField(
        default=False
    )
    receive_promotions = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.user.username}'s profile"