import django_filters as filters

from eggslist.blogs import models


class BlogFilter(filters.FilterSet):
    author = filters.NumberFilter(
        field_name="author__id", help_text="Id of a user who wrote the blog."
    )
    category = filters.CharFilter(
        field_name="category__slug", help_text="Slug of a category which needs to be filtered by."
    )

    class Meta:
        model = models.BlogArticle
        fields = ("author", "category")
