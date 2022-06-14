import typing as t

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.site_configuration.models import LocationCity
from eggslist.users.determine_location import locate_ip
from eggslist.users.password_reset_storage import PasswordResetStorage
from eggslist.utils.emailing import send_mailing
from . import constants, messages, serializers

if t.TYPE_CHECKING:
    from django.http.request import HttpRequest

User = get_user_model()


class SignInAPIView(GenericAPIView):
    serializer_class = serializers.SignInSerializer
    permission_classes = (~IsAuthenticated,)

    @staticmethod
    def login(request: "HttpRequest", email: str, password: str):
        user = authenticate(request=request, email=email, password=password)

        if not user:
            raise ValidationError({"message": messages.INVALID_CREDENTIALS})

        login(request=request, user=user)
        return user

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.login(request=request, **serializer.validated_data)
        return Response(status=200)


class SignUpAPIView(GenericAPIView):
    serializer_class = serializers.SignUpSerializer
    permission_classes = (~IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request=request, user=user)
        return Response(status=200)


class SignOutAPIView(APIView):
    """
    Remove Auth cookies
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        logout(request)
        return Response(status=200)


class UserProfileAPIView(RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class PasswordChangeAPIView(GenericAPIView):
    serializer_class = serializers.PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(raw_password=serializer.validated_data["password"])
        request.user.save()
        login(request=request, user=request.user)
        return Response(status=200)


class PasswordResetRequest(GenericAPIView):
    """
    Password Reset API. Backend will try to find the user given the email in the database and
    send secret link to the user.
    """

    serializer_class = serializers.PasswordResetRequestSerializer
    permission_classes = (~IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_code = PasswordResetStorage.generate_password_reset_code(
            email=serializer.validated_data["email"]
        )

        user = User.objects.get(email=serializer.validated_data["email"])
        password_reset_link = f"{settings.SITE_URL}/password-reset?reset_code={reset_code}"
        send_mailing(
            subject="Password Reset",
            mail_template="emails/password_reset.html",
            mail_object={"reset_link": password_reset_link},
            users=[user],
        )
        return Response(status=200)


class PasswordResetConfirm(GenericAPIView):
    """
    Password Reset Confirm API. Find a reset code associated to the particular user
    in the database
    """

    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = (~IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = PasswordResetStorage.authenticate_password_reset_code(
            reset_code=serializer.validated_data["reset_code"]
        )
        if not user:
            raise ValidationError({"reset_code": messages.RESET_CODE_NOT_FOUND})

        user.set_password(raw_password=serializer.validated_data["password"])
        user.save()
        return Response(status=200)


class LocationAPIView(RetrieveAPIView):
    """
    Location Retrieve API View. Return current user's location
    if backend application was not able to locate the user.
    This can happend if the one uses VPN, or using the website
    from outside of the US.
    """

    serializer_class = serializers.UserLocationSerializer

    def get_object(self):
        user_city_location_slug = self.request.COOKIES.get(constants.USER_LOCATION_COOKIE_NAME)
        if user_city_location_slug is not None:
            return LocationCity.objects.select_related("state__country").get(
                slug=user_city_location_slug
            )
        ip_address = self.request.META.get(
            "HTTP_X_FORWARDED_FOR", self.request.META.get("REMOTE_ADDR", "")
        )
        user_city_location = locate_ip(ip_address)

        return user_city_location

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response()

        serializer = self.get_serializer(instance)
        response = Response(serializer.data)
        response.set_cookie(constants.USER_LOCATION_COOKIE_NAME, value=instance.slug)
        return response


class SetLocationAPIView(GenericAPIView):
    """
    Set a location for the user when user explicitly provided it
    """

    serializer_class = serializers.SetLocationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city_location_instance = LocationCity.objects.get(slug=serializer.validated_data["slug"])
        response = Response()
        response.set_cookie(constants.USER_LOCATION_COOKIE_NAME, city_location_instance.slug)
        return response
