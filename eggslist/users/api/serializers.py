import typing as t

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from eggslist.blogs.models import BlogArticle
from eggslist.site_configuration.models import LocationCity, LocationZipCode
from eggslist.users import models
from eggslist.users.api import messages

User = get_user_model()


def validate_password(value: str):
    regex_validate = RegexValidator(
        regex=r"^(?=.*\d).{8,}",
        message=_(
            "Invalid password: it should have numeric symbols "
            "and be at least 8 characters length"
        ),
    )
    return regex_validate(value)


class SignInSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(required=True, style={"input_type": "password"})


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("email", "first_name", "password")

    def create(self, validated_data: t.Dict[str, t.Any]):
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError as e:
            print(e)
            raise serializers.ValidationError({"email": messages.EMAIL_ALREADY_EXISTS})


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"})


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text=_("User needs to provide an email which will be used to get a reset code")
    )

    def validate_email(self, value: str) -> str:
        value = value.lower()
        try:
            User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(messages.EMAIL_NOT_FOUND)
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"})
    code = serializers.CharField(
        required=True,
        help_text=_("User will get it in the email after they requested reset procedure"),
    )


class EmailVerifyConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True,
        help_text=_("The code user gets in the email message in order to verify themselves"),
    )


class UserLocationSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="name")
    state = serializers.CharField(source="state.name")
    country = serializers.CharField(source="state.country.name")
    lookup_radius = serializers.SerializerMethodField()
    is_undefined = serializers.SerializerMethodField()

    def get_lookup_radius(self, obj):
        return self.context["lookup_radius"]

    def get_is_undefined(self, obj):
        return self.context["is_undefined"]

    class Meta:
        model = LocationCity
        fields = ("slug", "city", "state", "country", "lookup_radius", "is_undefined")


class UserZipCodeLocationSerializer(serializers.ModelSerializer):
    zip_code = serializers.CharField(source="name")
    city = serializers.CharField(source="city.name")
    state = serializers.CharField(source="city.state.name")

    class Meta:
        model = LocationZipCode
        fields = ("zip_code", "city", "state")


class SetLocationSerializer(serializers.Serializer):
    slug = serializers.CharField(help_text=_("Slug of a city location object"))
    lookup_radius = serializers.IntegerField(
        help_text=_("A radius within we need to look the products for")
    )


class UserSerializerSmall(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "avatar",
        )


class UserSerializer(serializers.ModelSerializer):
    user_location = UserZipCodeLocationSerializer(
        required=False, read_only=True, source="zip_code"
    )
    is_email_verified = serializers.BooleanField(read_only=True)
    is_verified_seller = serializers.BooleanField(read_only=True)
    is_stripe_connected = serializers.BooleanField(
        source="stripe_connection.is_onboarding_completed", read_only=True
    )
    zip_code = serializers.SlugRelatedField(
        slug_field="slug", write_only=True, queryset=LocationZipCode.objects.all(), required=False
    )
    has_posted_blogs = serializers.SerializerMethodField()

    def get_has_posted_blogs(self, user):
        return BlogArticle.objects.filter(author=user).exists()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "user_location",
            "email",
            "is_email_verified",
            "is_verified_seller",
            "is_verified_seller_pending",
            "is_stripe_connected",
            "date_joined",
            "phone_number",
            "avatar",
            "bio",
            "zip_code",
            "has_posted_blogs",
        )


class OtherUserSerializerSmall(serializers.ModelSerializer):
    user_location = UserZipCodeLocationSerializer(read_only=True, source="zip_code")

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "phone_number", "avatar", "user_location")


class OtherUserSerializer(serializers.ModelSerializer):
    user_location = UserZipCodeLocationSerializer(
        required=False, read_only=True, source="zip_code"
    )
    is_favorite = serializers.BooleanField(read_only=True)
    has_posted_blogs = serializers.SerializerMethodField()

    def get_has_posted_blogs(self, user):
        return BlogArticle.objects.filter(author=user).exists()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "user_location",
            "email",
            "is_verified_seller",
            "date_joined",
            "phone_number",
            "avatar",
            "bio",
            "is_favorite",
            "has_posted_blogs",
        )


class VerifiedSellerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VerifiedSellerApplication
        fields = ("image", "text")
