from django.contrib.auth import get_user_model
from rest_framework import serializers

from eggslist.blogs import models

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("slug", "name")
        model = models.BlogCategory


class AuthorSerializerSmall(serializers.ModelSerializer):
    class Meta:
        fields = ("first_name", "last_name")
        model = User


class BlogSerializerSmall(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=models.BlogCategory.objects.all()
    )
    author = AuthorSerializerSmall(many=False, read_only=True)

    class Meta:
        fields = ("image", "title", "author", "category")
        model = models.BlogArticle
