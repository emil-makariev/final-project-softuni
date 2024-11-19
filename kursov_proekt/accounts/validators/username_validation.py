from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class UserNameValidatorTyping:
    def __init__(self, message=None):
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if value is None:
            self._message = 'Username can only contain letters, numbers, or underscores'
        else:
            self._message = value

    def __call__(self, value):
        if not all(letter.isalnum() or letter == '_' or letter == '.' for letter in value):
            raise ValidationError(self.message)
        return value


@deconstructible
class UserNameLengthValidator:
    def __init__(self, min_length=None, max_length=None, message=None):
        self.min_length = min_length
        self.max_length = max_length
        self.message = message

    @property
    def min_length(self):
        """Getter for min_length."""
        return self._min_length

    @min_length.setter
    def min_length(self, value):
        """Setter for min_length."""
        if value < 1:
            raise ValueError("Minimum length must be at least 1.")
        self._min_length = value

    @property
    def max_length(self):
        """Getter for max_length."""
        return self._max_length

    @max_length.setter
    def max_length(self, value):
        """Setter for max_length."""
        if value < self._min_length:
            raise ValueError("Maximum length cannot be less than minimum length.")
        self._max_length = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if value is None:
            self._message = f'Username must be between {self.min_length} and {self.max_length} characters.'
        else:
            self._message = value

    def __call__(self, value):
        """Apply the validation logic."""
        if len(value) < self._min_length or len(value) > self._max_length:
            raise ValidationError(self.message)
        return value


@deconstructible
class UsernameContainsNoSpacesValidator:
    def __init__(self, message=None):
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if value is None:
            self._message = "Username cannot contain spaces."
        else:
            self._message = value

    def __call__(self, value):
        if ' ' in value:
            raise ValidationError(self.message)
        return value
