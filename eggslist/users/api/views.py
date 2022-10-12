import typing as t

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from eggslist.site_configuration.models import LocationCity
from eggslist.users import models
from eggslist.users.determine_location import locate_ip
from eggslist.users.user_code_verify import PasswordResetCodeVerification, UserEmailVerification
from eggslist.users.user_location_storage import UserLocationStorage
from eggslist.utils.views.mixins import AnonymousUserIdAPIMixin, JWTMixin
from . import messages, serializers

if t.TYPE_CHECKING:
    from django.http.request import HttpRequest

User = get_user_model()


class SignInAPIView(GenericAPIView):
    """
    Deprecated
    """

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


class SignUpAPIView(JWTMixin, GenericAPIView):
    serializer_class = serializers.SignUpSerializer
    permission_classes = (~IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token_data = self.get_token_data(user=user)
        return Response(status=200, data=token_data)


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


class OtherUserProfileAPIView(RetrieveAPIView):
    serializer_class = serializers.OtherUserSerializer

    def get_queryset(self):
        return User.objects.get_for_user(user=self.request.user)


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
            raise ValidationError({"email": [messages.EMAIL_NOT_FOUND]})
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


class LocationAPIView(AnonymousUserIdAPIMixin, RetrieveAPIView):
    """
    Location Retrieve API View. Return current user's location
    Client gets empty response if backend application was not able to locate the user.
    This can happend if the one uses VPN, or using the website from outside of the US.
    """

    serializer_class = serializers.UserLocationSerializer

    def get_location_instance(self):
        user_city_location, _ = UserLocationStorage.get_user_location(user_id=self.get_user_id())

        if user_city_location is not None:
            return user_city_location

        ip_address = self.request.META.get(
            "HTTP_X_FORWARDED_FOR", self.request.META.get("REMOTE_ADDR", "")
        )
        user_city_location = locate_ip(ip_address)

        # This should be removed as it is designed only for dev purposes
        if self.request.query_params.get("r"):
            return LocationCity.objects.get(slug="boston")

        return user_city_location

    def retrieve(self, request, *args, **kwargs):
        location_instance = self.get_location_instance()

        if location_instance is None:
            return Response()

        serializer = self.get_serializer(location_instance)
        response = Response(serializer.data)

        UserLocationStorage.set_user_location(
            user_id=self.get_user_id(),
            city_location=location_instance,
            lookup_radius=settings.DEFAULT_LOOKUP_RADIUS,
        )

        return response


class SetLocationAPIView(AnonymousUserIdAPIMixin, GenericAPIView):
    """
    Set a location for the user when user explicitly provided it
    """

    serializer_class = serializers.SetLocationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city_location_instance = LocationCity.objects.get(slug=serializer.validated_data["slug"])
        UserLocationStorage.set_user_location(
            user_id=self.get_user_id(),
            city_location=city_location_instance,
            lookup_radius=serializer.validated_data["lookup_radius"],
        )
        return Response()


class BecomeVerifiedSellerAPIView(CreateAPIView):
    serializer_class = serializers.VerifiedSellerApplicationSerializer
    queryset = models.VerifiedSellerApplication

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChangeFavoriteStatus(APIView):
    """
    Add to favorite when user is not in `my favorite farmers`. Remove from
    favorites when user is in `my favorite farmers`
    """

    lookup_url_kwargs = "following_user"
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        following_user_id = self.kwargs[self.lookup_url_kwargs]
        models.UserFavoriteFarm.objects.create_or_delete(
            user_id=self.request.user.id, following_user_id=following_user_id
        )
        return Response(status=200)


class FavoriteUsersListAPIView(ListAPIView):
    """
    Return list of `my favorite farmers`
    """

    serializer_class = serializers.OtherUserSerializerSmall
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)
