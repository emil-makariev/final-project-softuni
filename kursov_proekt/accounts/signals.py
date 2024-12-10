from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings

from kursov_proekt.accounts.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created: bool, **kwargs):
    if created:

        # Create the Profile for the user
        Profile.objects.create(
            user=instance,
        )



