import secrets

from django.contrib.auth import get_user_model
from django.core.cache import cache


User = get_user_model()


class PasswordResetStorage:
    _PASSWORD_RESET_CODE_CACHE_KEY = "password_reset_code::{reset_code}"

    @classmethod
    def generate_password_reset_code(cls, email: str) -> str:
        reset_code = secrets.token_hex()
        cache.set(
            key=cls._PASSWORD_RESET_CODE_CACHE_KEY.format(reset_code=reset_code),
            value=email,
            timeout=1200,  # 20 min
        )
        return reset_code

    @classmethod
    def authenticate_password_reset_code(cls, reset_code: str) -> User:
        user_email = cache.get(
            key=cls._PASSWORD_RESET_CODE_CACHE_KEY.format(reset_code=reset_code)
        )
        try:
            return User.objects.get(email=user_email)
        except User.DoesNotExist:
            return
