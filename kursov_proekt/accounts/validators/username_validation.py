from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class UserNameValidationTyping:
    @deconstructible
    class UserNameValidator:
        def __init__(self, message="Username can only contain letters, numbers, or underscores"):
            self.message = message

        def __call__(self, value):
            if not all(letter.isalnum() or letter == '_' for letter in value):
                raise ValidationError(self.message)
            return value


@deconstructible
class UserNameLengthValidator:
    def __init__(self, min_length=3, max_length=20, message=None):
        self._min_length = min_length  # Private attributes for min and max length
        self._max_length = max_length
        self._message = message or f"Username must be between {self._min_length} and {self._max_length} characters."

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
        """Getter for the error message."""
        return self._message

    @message.setter
    def message(self, value):
        """Setter for the error message."""
        self._message = value

    def __call__(self, value):
        """Apply the validation logic."""
        if len(value) < self._min_length or len(value) > self._max_length:
            raise ValidationError(self.message)
        return value