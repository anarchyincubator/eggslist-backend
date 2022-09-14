import secrets

from django.db import models
from django.db.models import Field
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from eggslist.utils.models.lookups import NotEqual

Field.register_lookup(NotEqual)


class _SlugModelMixin:
    """
    Model inheriting from this mixin needs to have `slug_field_name`
    It should point to the field which is supposed to be used as a
    base for a slug.
    """

    def save(self, *args, **kwargs):
        if not self.slug:
            name = getattr(self, self.slug_field_name)

            self.slug = slugify(name)

            if self.slug_field_unique:
                filter_query = {}
                filter_query[self.slug_field_name] = name

                if self.__class__.objects.filter(**filter_query).exists():

                    extra = secrets.token_hex(6)
                    self.slug += f"_{extra}"

        super().save(*args, **kwargs)


class NameSlugModel(_SlugModelMixin, models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=64)
    slug = models.SlugField(verbose_name=_("slug"), max_length=128, unique=True)
    slug_field_name = "name"
    slug_field_unique = True

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class TitleSlugModel(_SlugModelMixin, models.Model):
    title = models.CharField(verbose_name=_("title"), max_length=256)
    slug = models.SlugField(verbose_name=_("slug"), max_length=512, unique=True)
    slug_field_name = "title"
    slug_field_unique = True

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
