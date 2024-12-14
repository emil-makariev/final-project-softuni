from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        custom_user_model = get_user_model()

        if username is None:
            username = kwargs.get(custom_user_model.USERNAME_FIELD)

        # Use the helper function to get the user
        searched_user = self.get_user_by_username_or_email(username)

        if searched_user and searched_user.check_password(password) and self.user_can_authenticate(searched_user):
            return searched_user

