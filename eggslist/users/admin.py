from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from eggslist.users import models
from eggslist.utils.admin import ImageAdmin


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "avatar",
                    "first_name",
                    "last_name",
                    "email",
                    "is_email_verified",
                    "is_verified_seller",
                    "bio",
                    "phone_number",
                    "zip_code",
                )
            },
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = DjangoUserAdmin.list_display


@admin.register(models.VerifiedSellerApplication)
class VerifiedSellerApplicationAdmin(ImageAdmin):
    list_display = ("user",)
    list_display_images = ("image",)
    readonly_fields = ("is_approved",)
