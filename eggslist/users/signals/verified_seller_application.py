from django.db.models.signals import post_save
from django.dispatch import receiver

from eggslist.users import models


@receiver(post_save, sender=models.VerifiedSellerApplication)
def apply_for_verified(
    sender, instance: models.VerifiedSellerApplication, created: bool, **kwargs
):
    if created:
        instance.user.is_verified_seller_pending = True
        instance.user.save()
    else:
        if instance.is_approved:
            instance.user.is_verified_seller_pending = False
            instance.user.is_verified_seller = True
