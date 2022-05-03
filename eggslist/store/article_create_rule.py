from django.db.models.signals import pre_save
from django.dispatch import receiver

from eggslist.store import models


class SellerNeedsMoreInfo(Exception):
    pass


@receiver(pre_save, sender=models.ProductArticle)
def check_user_info(sender, instance: models.ProductArticle, **kwargs):
    if not all(
        (
            instance.seller.first_name,
            instance.seller.last_name,
            instance.seller.zip_code,
            instance.seller.phone_number,
        )
    ):
        raise SellerNeedsMoreInfo()
