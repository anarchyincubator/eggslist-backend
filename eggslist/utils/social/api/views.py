import typing as t

from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.utils.social import auth_managers
from eggslist.utils.views.mixins import JWTMixin


class SocialAuthURLAPIView(APIView):
    """
    Get Social Authentication URL leading to third-party OAuth service to
    provide user authentication.
    """

    social_auth_manager_class: t.Type["auth_managers.SocialAuthManager"] = None

    def post(self, request, *args, **kwargs):
        social_auth_manager = self.social_auth_manager_class()
        social_url = social_auth_manager.get_authorization_url()
        return Response(status=200, data={"social_url": social_url})


class SocialAuthCallbackAPIView(JWTMixin, APIView):
    social_auth_manager_class: t.Type["auth_managers.SocialManager"] = None

    def get(self, request, *args, **kwargs):
        social_auth_manager = self.social_auth_manager_class()
        social_profile = social_auth_manager.get_social_profile(request.query_params)
        user = social_auth_manager.get_or_create_user(social_profile)
        token_data = self.get_token_data(user=user)
        return Response(status=200, data=token_data)


class GoogleAuthURLAPIView(SocialAuthURLAPIView):
    """
    Get Google OAuth URL leading to Google authentication system.
    Use this method to receive a URL. Redirect user to the provided URL.
    After authentication user will be redirected back to the website
    to callback URL with auth props.
    """

    social_auth_manager_class = auth_managers.GoogleSocialManager


class GoogleAuthCallbackAPIView(SocialAuthCallbackAPIView):
    """
    Use this method when user is redirected from Google authentication system.
    pass all of the google's props to this method.
    """

    social_auth_manager_class = auth_managers.GoogleSocialManager


class FacebookAuthURLAPIView(SocialAuthURLAPIView):
    """
    Get Facebook OAuth URL leading to Facebook authentication system.
    Use this method to receive a URL. Redirect user to the provided URL.
    After authentication user will be redirected back to the website
    to callback URL with auth props.
    """

    social_auth_manager_class = auth_managers.FacebookSocialManager


class FacebookAuthCallbackAPIView(SocialAuthCallbackAPIView):
    """
    Use this method when user is redirected from Facebook authentication system.
    pass all of the google's props to this method.

    """

    social_auth_manager_class = auth_managers.FacebookSocialManager
