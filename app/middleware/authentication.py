import secrets
import typing as t

from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware

if t.TYPE_CHECKING:
    from django.http import HttpRequest


class AnonymousIdAuthenticationMiddleware(AuthenticationMiddleware):
    """
    If the user is not authenticated assign a unique id to the user
    Modify AnonymousUser so it has an `id` field with a value of the generated
    key stored in session
    Recommended to use this Middleware with a Cookie session engine
    """

    def process_request(self, request: "HttpRequest"):
        super().process_request(request=request)
        if request.user.is_anonymous:
            unique_id = request.session.get(settings.ANONYMOUS_USER_ID_SESSION_KEY)

            if unique_id is None:
                unique_id = secrets.token_hex(6)
                request.session[settings.ANONYMOUS_USER_ID_SESSION_KEY] = unique_id
