from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin, messages
from django.db.models import Count, DateTimeField, F, Max, Min, Sum, Value
from django.db.models.functions import Trunc
from django.utils.translation import ngettext

from eggslist.store import models
from eggslist.utils.admin import ImageAdmin


class SubcategoryInline(admin.StackedInline):
    model = models.Subcategory
    extra = 1
    exclude = ("slug",)


@admin.register(models.Category)
class CategoryAdmin(SortableAdminMixin, ImageAdmin):
    list_display = ("position", "name", "subcategories")
    list_display_images = ("image",)
    readonly_fields = ("slug",)
    inlines = (SubcategoryInline,)
    ordering = ("position",)

    def subcategories(self, obj):
        return ", ".join([x.name for x in obj.subcategories.all()])


@admin.register(models.Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_select_related = ("category",)
    readonly_fields = ("slug",)


@admin.register(models.ProductArticle)
class ProductArticleAdmin(ImageAdmin):
    list_display = (
        "title",
        "subcategory",
        "seller",
        "is_hidden",
        "is_out_of_stock",
        "is_banned",
        "is_archived",
    )
    list_display_images = ("image",)
    list_select_related = ("seller", "subcategory__category")
    readonly_fields = ("engagement_count", "date_created", "slug")
    search_fields = (
        "id",
        "subcategory__name",
        "subcategory__category__name",
        "seller__email",
        "seller__first_name",
        "seller__last_name",
        "title",
        "description",
    )
    list_filter = (
        "is_hidden",
        "is_out_of_stock",
        "is_banned",
        "is_archived",
        "date_created",
        "subcategory__category",
    )
    ordering = ("is_archived",)
    actions = ("mark_as_archived", "unmark_as_archived")


    def mark_as_archived(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(
            request,
            ngettext(
                "%d product article was marked as archived.",
                "%d product articles were marked as archived.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    def unmark_as_archived(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(
            request,
            ngettext(
                "%d product article was unmarked as archived",
                "%d product articles were unmarked as archived",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "customer",
        "customer_email",
        "product",
        "price",
        "seller",
        "created_at",
        "modified_at",
    )
    readonly_fields = list_display + ("stripe_connection", "payment_intent")
    search_fields = ("product", "price", "seller", "customer", "customer_email", "payment_intent")
    list_filter = (
        "status",
        "created_at",
    )

    def has_add_permission(self, request):
        return False


@admin.register(models.SaleStatistic)
class SalesStatisticsAdmin(admin.ModelAdmin):
    change_list_template = "admin/dashboard/sales_change_list.html"
    actions = None
    date_hierarchy = "created_at"
    list_select_related = ("product__subcategory__category",)
    show_full_result_count = False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    @staticmethod
    def get_next_in_date_hierarchy(request, date_hierarchy):
        if date_hierarchy + "__day" in request.GET:
            return "hour"
        if date_hierarchy + "__month" in request.GET:
            return "day"
        if date_hierarchy + "__year" in request.GET:
            return "week"
        return "month"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            qs = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {"total": Count("id"), "total_sales": Sum("price")}
        summary_total = qs.aggregate(**metrics)
        metrics_ann = {
            **metrics,
            "total_sales_perc": (Sum("price") / Value(summary_total["total_sales"]) * 100),
        }
        response.context_data["summary"] = list(
            qs.values("product__subcategory__category__name")
            .annotate(**metrics_ann)
            .order_by("-total_sales")
        )
        # List view summary
        response.context_data["summary_total"] = summary_total

        # Chart
        period = self.get_next_in_date_hierarchy(request, self.date_hierarchy)
        print(period)
        response.context_data["period"] = period
        summary_over_time = (
            qs.annotate(period=Trunc("created_at", period, output_field=DateTimeField()))
            .values("period")
            .annotate(total=Sum("price"))
            .order_by("period")
        )
        summary_range = summary_over_time.aggregate(
            high=Max("total"),
        )
        summary_range["low"] = 0
        high = summary_range.get("high", 0)
        low = summary_range.get("low", 0)

        response.context_data["summary_over_time"] = [
            {
                "period": x["period"],
                "total": x["total"] or 0,
                "pct": ((x["total"] or 0) - low) / (high - low) * 100 if high > low else 0,
            }
            for x in summary_over_time
        ]

        return response
