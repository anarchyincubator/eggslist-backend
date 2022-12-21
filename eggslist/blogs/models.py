from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from eggslist.blogs.managers import BlogManager
from eggslist.utils.models import NameSlugModel, TitleSlugModel


class BlogCategory(NameSlugModel):
    class Meta:
        verbose_name = _("blog category")
        verbose_name_plural = _("blog categories")


class BlogArticle(TitleSlugModel):
    image = ProcessedImageField(
        upload_to="blogs",
        processors=[ResizeToFill(410, 270)],
        format="JPEG",
        options={"quality": 75},
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        verbose_name=_("author"), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        verbose_name=_("category"), to="BlogCategory", on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(verbose_name=_("date created"), auto_now_add=True)
    body = CKEditor5Field(verbose_name=_("body"), config_name="default")

    objects = BlogManager()

    class Meta:
        verbose_name = _("blog article")
        verbose_name_plural = _("blog articles")
