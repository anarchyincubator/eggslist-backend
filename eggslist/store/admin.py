from django.contrib import admin

from eggslist.store import models
from eggslist.utils.admin import ImageAdmin


class SubcategoryInline(admin.StackedInline):
    model = models.Subcategory
    extra = 1
    exclude = ("slug",)


@admin.register(models.Category)
class CategoryAdmin(ImageAdmin):
    list_display = ("name", "subcategories")
    list_display_images = ("image",)
    readonly_fields = ("slug",)
    inlines = (SubcategoryInline,)

    def subcategories(self, obj):
        return ", ".join([x.name for x in obj.subcategories.all()])


@admin.register(models.Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_select_related = ("category",)
    readonly_fields = ("slug",)


@admin.register(models.ProductArticle)
class ProductArticleAdmin(ImageAdmin):
    list_display = ("title", "subcategory", "seller", "seller_status", "is_banned")
    list_display_images = ("image",)
    list_select_related = ("seller", "subcategory")
    readonly_fields = ("engagement_count", "date_created", "slug")


@admin.register(models.UserViewTimestamp)
class ProductUserView(admin.ModelAdmin):
    list_display = ("user", "timestamp", "product")
