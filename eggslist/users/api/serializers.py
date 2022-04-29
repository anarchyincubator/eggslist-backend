from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()


def validate_password(value):
    regex_validate = RegexValidator(
        regex=r"^(?=.*\d).{8,}",
        message=_(
            "Invalid password: it should have numeric symbols "
            "and be at least 8 characters length"
        ),
    )
    return regex_validate(value)


class NewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, style={"input_type": "password"})
    password_repeat = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_repeat"):
            raise serializers.ValidationError({"password": "Passwords are not the same"})

        attrs.pop("password_repeat")
        return super().validate(attrs)


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(
        help_text=_(
            "User can submit either a username or email here. "
            "Backend will automatically look for both"
        )
    )
    password = serializers.CharField(required=True, style={"input_type": "password"})


class SignUpSerializer(NewPasswordSerializer):
    username = serializers.CharField(
        allow_null=True,
        help_text=_("If not provided Backend will automatically use email as username"),
    )
    email = serializers.EmailField()

    def create(self, validated_data):
        username = validated_data.pop("username")
        username = username or validated_data["email"]
        return User.objects.create_user(username=username, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "is_verified_seller", "avatar", "bio")


class PasswordChangeSerializer(NewPasswordSerializer):
    pass


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text=_("User needs to provide an email which will be " "used to get a reset code")
    )

    def validate_email(self, value: str) -> str:
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": _("User with this email was not found")})
        return value


class PasswordResetConfirmSerializer(NewPasswordSerializer):
    reset_code = serializers.CharField(
        required=True,
        help_text=_("User will get it in the email after they " "requested reset procedure"),
    )
