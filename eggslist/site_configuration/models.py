from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from eggslist.utils.models import NameSlugModel


class LocationStateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("country")


class LocationCityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("state__country")


class LocationZipCodeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("city__state__country")


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
    objects = LocationStateManager()

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
    objects = LocationCityManager()

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
    system_name = models.CharField(verbose_name=_("system name"), max_length=64, default="")
    objects = LocationZipCodeManager()

    class Meta:
        verbose_name = _("location zip code")
        verbose_name_plural = _("location zip codes")


class Testimonial(models.Model):
    author_name = models.CharField(verbose_name=_("author name"), max_length=32)
    body = models.TextField(verbose_name=_("body"))

    class Meta:
        verbose_name = _("testimonial")
        verbose_name_plural = _("testimonials")

    def __str__(self):
        return f"{self.author_name} -- {self.body[:40]}..."


class FAQ(models.Model):
    question = models.CharField(verbose_name=_("question"), max_length=256)
    answer = models.TextField(verbose_name=_("answer"))

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class TeamMember(models.Model):
    first_name = models.CharField(verbose_name=_("first name"), max_length=128)
    last_name = models.CharField(verbose_name=_("last name"), max_length=128)
    image = ProcessedImageField(
        upload_to="about",
        processors=[ResizeToFill(300, 300)],
        format="JPEG",
        options={"quality": 70},
    )
    job_title = models.CharField(verbose_name=_("job title"), max_length=128)

    class Meta:
        verbose_name = _("team member")
        verbose_name_plural = _("team members")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
