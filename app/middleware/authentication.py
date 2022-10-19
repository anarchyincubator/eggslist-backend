import secrets
import typing as t

from django.conf import settings

if t.TYPE_CHECKING:
    from django.http import HttpRequest


class AnonymousIdAuthenticationMiddleware:
    def __init__(self, get_response: t.Callable):
        self.get_response = get_response

    def __call__(self, request: "HttpRequest"):
        anon_user_id = request.COOKIES.get(settings.ANONYMOUS_USER_ID_COOKIE, None)

        if request.user.is_anonymous and anon_user_id is None:
            anon_user_id = secrets.token_hex(6)
            request.COOKIES[settings.ANONYMOUS_USER_ID_COOKIE] = anon_user_id
            response = self.get_response(request)
            response.set_cookie(settings.ANONYMOUS_USER_ID_COOKIE, anon_user_id)
            return response
        elif (
            request.user.is_authenticated
            and request.COOKIES.get(settings.ANONYMOUS_USER_ID_COOKIE) is not None
        ):
            response = self.get_response(request)
            response.delete_cookie(settings.ANONYMOUS_USER_ID_COOKIE)
            return response

        response = self.get_response(request)
        return response
