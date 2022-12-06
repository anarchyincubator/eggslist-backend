import django_filters as filters
from django import forms
from django.conf import settings
from django.db.utils import DatabaseError

from eggslist.site_configuration.models import LocationZipCode
from eggslist.store import models

if settings.DEBUG:
    try:
        subcategory_choices = [(obj.slug, obj.slug) for obj in models.Subcategory.objects.all()]
        zip_code_choices = [(obj.name, obj.name) for obj in LocationZipCode.objects.all()]
    except DatabaseError:
        subcategory_choices = zip_code_choices = []
else:
    subcategory_choices = zip_code_choices = []


class NonValidatingMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class NonValidatingMultipleChoiceFilter(filters.MultipleChoiceFilter):
    field_class = NonValidatingMultipleChoiceField


class FavoriteFarmOrderingFilter(filters.OrderingFilter):
    """
    It works with a queryset of ProductArticle with annotated field name `seller__is_favorite`
    """

    def filter(self, qs, value):
        if not value:
            return qs

        ordering = [self.get_ordering_value(param) for param in value]

        if any(v in ["relevance", "-relevance"] for v in value):
            ordering = ["-seller__is_favorite"] + ordering

        return qs.order_by(*ordering)


class ProductFilter(filters.FilterSet):
    price_from = filters.NumberFilter(
        field_name="price", lookup_expr="gt", help_text="Minimum price field."
    )
    price_to = filters.NumberFilter(
        field_name="price", lookup_expr="lt", help_text="Maximum price field."
    )
    subcategory = NonValidatingMultipleChoiceFilter(
        field_name="subcategory__slug",
        choices=subcategory_choices,
        help_text="Subcategory's slug which user wants to get. Can be used multiple times \n e.g '.?subcategory=chicken-eggs&subcategory=goose-eggs'.",
    )
    ordering = FavoriteFarmOrderingFilter(
        choices=(
            ("relevance", "Relevance"),
            ("price", "Price"),
            ("-price", "Price (descending)"),
            ("date_create", "Date Created"),
            ("-date_created", "Date Created (descending)"),
        ),
        fields={
            "price": "price",
            "date_created": "date_created",
            "-engagement_count": "relevance",
        },
    )

    class Meta:
        model = models.ProductArticle
        fields = ("subcategory", "allow_pickup", "allow_delivery")
