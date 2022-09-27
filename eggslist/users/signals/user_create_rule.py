from django.db.models.signals import post_save
from django.dispatch import receiver

from eggslist.users import models
from eggslist.users.user_code_verify import UserEmailVerification


@receiver(post_save, sender=models.User)
def send_email_verification_request(sender, instance: models.User, created: bool, **kwargs):
    if created:
        UserEmailVerification.generate_and_send_email_code(user=instance)
