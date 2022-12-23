from django.contrib import admin

from eggslist.blogs import models
from eggslist.utils.admin import ImageAdmin


@admin.register(models.BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    readonly_fields = ("slug",)


@admin.register(models.BlogArticle)
class BlogArticleAdmin(ImageAdmin):
    summernote_fields = ("body",)
    list_display = ("title", "category")
    list_display_images = ("image",)
    list_select_related = ("category",)
    readonly_fields = ("slug",)
