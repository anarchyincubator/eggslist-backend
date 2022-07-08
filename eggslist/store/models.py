from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from eggslist.store import constants
from eggslist.store.managers import ProductArticlManager
from eggslist.utils.models import NameSlugModel, TitleSlugModel


class Category(NameSlugModel):
    image = ProcessedImageField(
        upload_to="categories",
        processors=[ResizeToFill(300, 140)],
        format="JPEG",
        options={"quality": 70},
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class Subcategory(NameSlugModel):
    category = models.ForeignKey(
        verbose_name=_("category"),
        to="Category",
        related_name="subcategories",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("subcategory")
        verbose_name_plural = _("subcategories")
        constraints = (
            models.constraints.UniqueConstraint(
                name="unique_subcategory", fields=("name", "category")
            ),
        )


class ProductArticle(TitleSlugModel):
    description = models.TextField(verbose_name=_("description"))
    subcategory = models.ForeignKey(
        verbose_name=_("subcategory"), to="Subcategory", on_delete=models.CASCADE
    )
    image = ProcessedImageField(
        upload_to="product_articles",
        processors=[ResizeToFill(500, 500)],
        format="JPEG",
        options={"quality": 75},
    )
    price = models.DecimalField(verbose_name=_("price"), max_digits=8, decimal_places=2)
    date_created = models.DateTimeField(verbose_name=_("date created"), auto_now_add=True)
    allow_pickup = models.BooleanField(verbose_name=_("allow pickup"), default=True)
    allow_delivery = models.BooleanField(verbose_name=_("allow delivery"), default=False)
    seller = models.ForeignKey(
        verbose_name=_("seller"),
        to=settings.AUTH_USER_MODEL,
        related_name="product_articles",
        on_delete=models.CASCADE,
    )
    is_banned = models.BooleanField(verbose_name=_("is banned"), default=False)
    seller_status = models.CharField(
        verbose_name=_("seller status"),
        max_length=32,
        choices=constants.SELLER_STATUS,
        default=constants.ACTIVE,
    )
    engagement_count = models.PositiveIntegerField(
        verbose_name=_("engagement count"),
        help_text=_("Nubmer of clicks on `Contact` button in the product page"),
        default=0,
    )
    objects = ProductArticlManager()

    class Meta:
        verbose_name = _("product article")
        verbose_name_plural = _("product articles")
