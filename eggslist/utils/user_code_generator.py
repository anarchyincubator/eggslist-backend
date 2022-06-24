import secrets
import typing as t

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from eggslist.utils.emailing import send_mailing

User = get_user_model()


class EmailCodeVerification:
    """
    Create a user code which has to be verified through email
    """

    code_cache_key = None
    code_ttl = 1200  # 20 min
    link_endpoint = None
    link_param_key = None
    mail_subject = None
    mail_template = None

    @classmethod
    def _get_cache_key(cls, code):
        return f"email_code::{cls.code_cache_key}::{code}"

    @classmethod
    def generate_code(cls, email: str):
        code = secrets.token_hex()
        cache.set(key=cls._get_cache_key(code), value=email, timeout=cls.code_ttl)
        return code

    @classmethod
    def verify_email_code(cls, code: str) -> t.Optional[User]:
        user_email = cache.get(key=cls._get_cache_key(code))
        try:
            return User.objects.get(email=user_email)
        except User.DoesNotExist:
            return

    @classmethod
    def generate_and_send_email_code(cls, email) -> str:
        code = cls.generate_code(email=email)
        user_code_link = f"{settings.SITE_URL}/{cls.link_endpoint}?{cls.link_param_key}={code}"
        user = User.objects.get(email=email)
        send_mailing(
            subject=cls.mail_subject,
            mail_template=cls.mail_template,
            mail_object={"user_code_link": user_code_link},
            users=[user],
        )
        return code
