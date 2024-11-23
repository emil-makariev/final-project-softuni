from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kursov_proekt.accounts'

    def ready(self):
        import kursov_proekt.accounts.signals