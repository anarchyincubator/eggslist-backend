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


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField(help_text=_("Username can be either username or email"))
    password = serializers.CharField(required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("username", "password")
