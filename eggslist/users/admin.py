from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from eggslist.users import constants, models
from eggslist.utils.admin import ImageAdmin


@admin.register(models.UserStripeConnection)
class StripeConnectionAdmin(admin.ModelAdmin):
    list_display = ("stripe_account", "user", "is_onboarding_completed")
    list_filter = ("is_onboarding_completed",)
    search_fields = ("stripe_account", "user")
    readonly_fields = ("stripe_account",)


class StripeConnectionAdminInline(admin.TabularInline):
    model = models.UserStripeConnection
    can_delete = False
    readonly_fields = ("is_onboarding_completed",)
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    readonly_fields = ("is_stripe_connected", "date_joined", "last_login")
    autocomplete_fields = ("zip_code",)
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
                    "is_stripe_connected",
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
    list_display = DjangoUserAdmin.list_display + ("date_joined",)
    inlines = (StripeConnectionAdminInline,)
    search_fields = ("email", "first_name", "last_name", "bio")
    list_filter = (
        "date_joined",
        "is_email_verified",
        "is_verified_seller",
        "stripe_connection__is_onboarding_completed",
        "zip_code__city__state",
    )

    @admin.display(boolean=True)
    def is_stripe_connected(self, obj):
        return bool(obj.stripe_connection.is_onboarding_completed)


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
