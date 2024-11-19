from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        custom_user_model = get_user_model()

        if username is None:
            username = kwargs.get(custom_user_model.USERNAME_FIELD)
        try:
            searched_user = custom_user_model.objects.get(email=username)
        except custom_user_model.DoesNotExist:
            try:
                searched_user = custom_user_model.objects.get(name=username)
            except custom_user_model.DoesNotExist:
                return None

        if searched_user.check_password(password) and self.user_can_authenticate(searched_user):
            return searched_user

