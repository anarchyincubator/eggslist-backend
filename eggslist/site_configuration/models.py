from django.db import models
from django.utils.translation import gettext_lazy as _

from eggslist.utils.models import NameSlugModel


class LocationCountry(NameSlugModel):
    class Meta:
        verbose_name = _("location country")
        verbose_name_plural = _("location countries")


class LocationState(NameSlugModel):
    country = models.ForeignKey(
        verbose_name=_("country"),
        to="LocationCountry",
        related_name="states",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("location state")
        verbose_name_plural = _("location states")


class LocationCity(NameSlugModel):
    state = models.ForeignKey(
        verbose_name=_("state"),
        to="LocationState",
        related_name="cities",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("location city")
        verbose_name_plural = _("location cities")


class LocationZipCode(NameSlugModel):
    city = models.ForeignKey(
        verbose_name=_("city"),
        to="LocationCity",
        related_name="zip_codes",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("location zip code")
        verbose_name_plural = _("location zip codes")
