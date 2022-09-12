from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from eggslist.users import constants, models
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
    list_display = ("user", "status", "text")
    list_display_images = ("image",)
    list_select_related = ("user",)
    readonly_fields = ("status",)

    actions = ("approve", "refuse")

    def approve(self, request, queryset):
        qs_users = models.User.objects.filter(id__in=queryset.values("user_id"))
        updated = queryset.update(status=constants.APPROVED)
        qs_users.update(is_verified_seller=True, is_verified_seller_pending=False)

        self.message_user(
            request,
            ngettext(
                "%d user was successfully marked as verified.",
                "%d users were successfully marked as verified.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    def refuse(self, request, queryset):
        qs_users = models.User.objects.filter(id__in=queryset.values("user_id"))
        updated = queryset.update(status=constants.REFUSED)
        qs_users.update(is_verified_seller=False, is_verified_seller_pending=False)

        self.message_user(
            request,
            ngettext(
                "%d user was successfully marked as not verified.",
                "%d users were successfully marked as not verified.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )
