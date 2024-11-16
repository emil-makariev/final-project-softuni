from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from kursov_proekt.accounts.manager import CustomUserManager
from kursov_proekt.accounts.validators.username_validation import UserNameValidationTyping, UserNameLengthValidator


class CustomUser(AbstractBaseUser, PermissionsMixin):
    MAX_LENGTH = 20
    MIN_LENGTH = 3
    username = models.CharField(
        validators=(
            UserNameValidationTyping(),
            UserNameLengthValidator(MIN_LENGTH, MAX_LENGTH),
        )
    )
    email = models.EmailField(

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
        ),
    ),

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()


