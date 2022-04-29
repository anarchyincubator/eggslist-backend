from django.contrib.auth import get_user_model
from rest_framework import serializers

from eggslist.site_configuration.models import LocationZipCode
from eggslist.store import models

User = get_user_model()


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = models.Subcategory


class LocationSerializer(serializers.ModelSerializer):
    zipcode = serializers.CharField(read_only=True, source="name")
    city = serializers.CharField(read_only=True, source="city.name")
    state = serializers.CharField(read_only=True, source="city.state.name")

    class Meta:
        model = LocationZipCode
        fields = ("zipcode", "city", "state")


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True)

    class Meta:
        fields = ("name", "image", "subcategories")
        model = models.Category


class SellerSerializerSmall(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class SellerSerializer(serializers.ModelSerializer):
    location = LocationSerializer(source="zip_code")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "is_verified_seller", "location")


class ProductArticleSerializerSmall(serializers.ModelSerializer):
    seller = SellerSerializerSmall(read_only=True)

    class Meta:
        model = models.ProductArticle
        fields = ("title", "image", "slug", "price", "seller")


class ProductArticleSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    is_banned = serializers.BooleanField(read_only=True)
    seller = SellerSerializer(many=False, read_only=True)
    subcategory = serializers.SlugRelatedField(
        slug_field="name", queryset=models.Category.objects.all()
    )
    location = LocationSerializer(source="seller.zip_code")

    class Meta:
        fields = (
            "title",
            "image",
            "slug",
            "description",
            "subcategory",
            "date_created",
            "allow_pickup",
            "allow_delivery",
            "price",
            "seller",
            "is_banned",
            "seller_status",
            "location",
        )
        model = models.ProductArticle
