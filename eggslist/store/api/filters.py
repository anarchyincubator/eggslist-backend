import django_filters as filters
from django import forms
from django.conf import settings

from eggslist.site_configuration.models import LocationZipCode
from eggslist.store import models

if settings.DEBUG:
    subcategory_choices = [(obj.slug, obj.slug) for obj in models.Subcategory.objects.all()]
    zip_code_choices = [(obj.name, obj.name) for obj in LocationZipCode.objects.all()]
else:
    subcategory_choices = zip_code_choices = []


class NonValidatingMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class NonValidatingMultipleChoiceFilter(filters.MultipleChoiceFilter):
    field_class = NonValidatingMultipleChoiceField


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
    zip_code = NonValidatingMultipleChoiceFilter(
        choices=zip_code_choices,
        help_text="zip_code to filter by",
        field_name="seller__zip_code__name",
    )

    class Meta:
        model = models.ProductArticle
        fields = ("subcategory", "zip_code", "allow_pickup", "allow_delivery")
