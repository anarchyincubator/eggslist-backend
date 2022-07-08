import typing as t

from django.contrib.auth import authenticate, get_user_model, login, logout
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from eggslist.site_configuration.models import LocationCity
from eggslist.users.determine_location import locate_ip
from eggslist.users.user_code_verify import PasswordResetCodeVerification, UserEmailVerification
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


class JWTSignInAPIView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data.pop("refresh")
        return response


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


class UserProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserProfileLocationAPIView(GenericAPIView):
    """
    Do not mix up this method with Set Location API method. This method is responsible for
    a user profile location information. This location is stored in database and necessary for
    sellers to show where their goods are.
    """

    serializer_class = serializers.SetUserZipCodeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User.objects.update_location(
            email=request.user.email, zip_code_slug=serializer.validated_data["zip_code"]
        )
        return Response(status=200)


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
        try:
            PasswordResetCodeVerification.generate_and_send_email_code(
                email=serializer.validated_data["email"]
            )
        except User.DoesNotExist:
            raise ValidationError({"email": messages.EMAIL_NOT_FOUND})
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
        user = PasswordResetCodeVerification.verify_email_code(
            code=serializer.validated_data["code"]
        )
        if not user:
            raise ValidationError({"code": messages.RESET_CODE_NOT_FOUND})

        user.set_password(raw_password=serializer.validated_data["password"])
        user.save()
        return Response(status=200)


class EmailVerifyRequestAPIView(APIView):
    """
    Request an email verification email with a link to follow up to verify it
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        UserEmailVerification.generate_and_send_email_code(email=self.request.user.email)
        return Response(status=200)


class EmailVerifyConfirmAPIView(GenericAPIView):
    """
    Verify User email from using a code sent to a user's email after sign up or on demand
    """

    serializer_class = serializers.EmailVerifyConfirmSerializer

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserEmailVerification.verify_email_code(code=serializer.validated_data["code"])
        if not user:
            raise ValidationError({"code": messages.EMAIL_VERIFICATION_CODE_NOT_FOUND})

        User.objects.verify_email(email=user.email)
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
