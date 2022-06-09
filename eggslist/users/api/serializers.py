import typing as t

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from eggslist.site_configuration.models import LocationCity
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "is_verified_seller", "avatar", "bio")


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"})


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text=_("User needs to provide an email which will be " "used to get a reset code")
    )

    def validate_email(self, value: str) -> str:
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": messages.EMAIL_NOT_FOUND})
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"})
    reset_code = serializers.CharField(
        required=True,
        help_text=_("User will get it in the email after they requested reset procedure"),
    )


class UserLocationSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="name", read_only=True)
    state = serializers.CharField(source="state.name", read_only=True)
    country = serializers.CharField(source="state.country.name", read_only=True)

    class Meta:
        model = LocationCity
        fields = ("city", "state", "country")
