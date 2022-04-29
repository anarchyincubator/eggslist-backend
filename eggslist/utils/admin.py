import typing

from django.contrib import admin
from django.utils.safestring import mark_safe


class ImageAdmin(admin.ModelAdmin):
    list_display_images: typing.Iterable[str] = ()
    list_display_images_custom_order = False

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if not self.list_display_images_custom_order:
            list_display += tuple(f"{image_field}_tag" for image_field in self.list_display_images)
        return list_display

    @classmethod
    def get_image_tag_func(cls, image_field: str, field_short_description: str):
        def func(obj):
            image = getattr(obj, image_field)
            if image:
                return mark_safe(
                    f"<img src='{image.url}' "
                    f"style='max-width: 150px; max-height: 60px; object-fit: contain;'>"
                )
            else:
                return None

        setattr(func, "short_description", field_short_description)
        return func

    def __getattr__(self, attr):
        try:
            return super().__getattr__(attr)
        except AttributeError:
            pass

        if not attr.endswith("_tag"):
            raise AttributeError

        field_name = attr[:-4]  # skip '_tag'
        if field_name not in self.list_display_images:
            raise AttributeError

        # retrieve verbose_name of field
        field_short_description = self.model._meta.get_field(field_name).verbose_name
        return self.get_image_tag_func(field_name, field_short_description)
