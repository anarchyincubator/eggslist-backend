from django.contrib.auth import get_user_model
from rest_framework import serializers

from eggslist.blogs import models
from eggslist.site_configuration.models import LocationZipCode

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("slug", "name")
        model = models.BlogCategory


class AuthorSerializerSmall(serializers.ModelSerializer):
    class Meta:
        fields = ("first_name", "last_name", "id")
        model = User


class AuthorLocationSerializer(serializers.ModelSerializer):
    zipcode = serializers.CharField(read_only=True, source="name")
    city = serializers.CharField(read_only=True, source="city.name")
    state = serializers.CharField(read_only=True, source="city.state.name")

    class Meta:
        model = LocationZipCode
        fields = ("zipcode", "city", "state")


class AuthorSerializer(serializers.ModelSerializer):
    location = AuthorLocationSerializer(source="zip_code")

    class Meta:
        fields = ("first_name", "last_name", "id", "location", "avatar", "phone_number", "email")
        model = User


class BlogSerializerSmall(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    author = AuthorSerializerSmall(many=False, read_only=True)

    class Meta:
        fields = ("image", "title", "slug", "author", "category")
        model = models.BlogArticle


class BlogSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    author = AuthorSerializer(many=False, read_only=True)
    slug = serializers.SlugField(read_only=True)
    category_slug = serializers.SlugRelatedField(
        slug_field="slug",
        write_only=True,
        queryset=models.BlogCategory.objects.all(),
        source="category",
    )
    similar_blogs = serializers.SerializerMethodField()

    def get_similar_blogs(self, obj):
        qs = models.BlogArticle.objects.get_similar_for(obj)
        return BlogSerializerSmall(qs, many=True).data

    class Meta:
        fields = (
            "image",
            "title",
            "slug",
            "author",
            "category",
            "body",
            "category_slug",
            "similar_blogs",
            "date_created",
        )
        model = models.BlogArticle
