import random

from django.contrib.auth import get_user_model
from rest_framework import serializers

from eggslist.site_configuration.models import LocationZipCode
from eggslist.store import article_create_rule, models
from eggslist.store.api import messages

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
    is_favorite = serializers.SerializerMethodField()

    def get_is_favorite(self, obj):
        # This is only for dev purposes. Remove it when implement fav farms
        return bool(random.getrandbits(1))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_verified_seller", "is_favorite")


class SellerSerializer(serializers.ModelSerializer):
    location = LocationSerializer(source="zip_code")

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "avatar",
            "phone_number",
            "is_verified_seller",
            "location",
        )


class ProductArticleSerializerSmall(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    seller = SellerSerializerSmall(read_only=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = models.ProductArticle
        fields = ("title", "image", "slug", "price", "seller")


class ProductArticleSerializerSmallMy(serializers.ModelSerializer):
    seller = SellerSerializerSmall(read_only=True)

    class Meta:
        model = models.ProductArticle
        fields = ("title", "image", "slug", "price", "seller", "is_hidden", "is_out_of_stock")


class ProductArticleSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    is_banned = serializers.BooleanField(read_only=True)
    seller = SellerSerializer(many=False, read_only=True)
    subcategory = serializers.SlugRelatedField(
        slug_field="name", queryset=models.Subcategory.objects.all()
    )
    you_may_also_like = serializers.SerializerMethodField()
    more_from_this_farm = serializers.SerializerMethodField()

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
            "you_may_also_like",
            "more_from_this_farm",
        )
        model = models.ProductArticle

    def get_you_may_also_like(self, obj):
        qs = models.ProductArticle.objects.get_best_similar_for(obj)
        return ProductArticleSerializerSmall(qs, many=True).data

    def get_more_from_this_farm(self, obj):
        qs = models.ProductArticle.objects.get_from_the_same_farm_for(obj)
        return ProductArticleSerializerSmall(qs, many=True).data

    def create(self, validated_data):
        try:
            return models.ProductArticle.objects.create(**validated_data)
        except article_create_rule.SellerNeedsMoreInfo:
            raise serializers.ValidationError({"popup": messages.SELLER_NEEDS_MORE_INFO})
        except article_create_rule.SellerNeedsEmailVerification:
            raise serializers.ValidationError({"popup": messages.SELLER_NEEDS_EMAIL_VERIFICATION})
