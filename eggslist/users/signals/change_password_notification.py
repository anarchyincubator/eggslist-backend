from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from eggslist.users import models
from eggslist.utils.emailing import send_mailing


@receiver(post_save, sender=models.User)
def send_change_password_notification(sender, instance: models.User, created: bool, **kwargs):
    if not created and getattr(instance, "_set_password", False):
        send_mailing(
            subject="Password Changed",
            mail_template="emails/change_password_notification.html",
            mail_object={"site_url": settings.SITE_URL},
            users=[instance],
        )
        instance._set_password = False
