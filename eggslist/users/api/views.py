import typing as t

import stripe
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.utils import IntegrityError
from django.http import Http404
from django.shortcuts import redirect
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
from eggslist.users.permissions import IsVerifiedSeller
from eggslist.users.user_code_verify import PasswordResetCodeVerification, UserEmailVerification
from eggslist.users.user_location_storage import UserLocationStorage
from eggslist.utils.emailing import send_mailing
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
    Deprecated
    Remove Auth cookies
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: "HttpRequest", *args, **kwargs):
        logout(request)
        return Response(status=200)


class UserSmallProfileView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializerSmall
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        # Stripe verify if onboarding completed
        user = self.request.user
        if (
            hasattr(user, "stripe_connection")
            and not user.stripe_connection.is_onboarding_completed
        ):
            account = stripe.Account.retrieve(user.stripe_connection.stripe_account)
            if account.details_submitted:
                user.stripe_connection.is_onboarding_completed = True
                user.stripe_connection.save()
                send_mailing(
                    subject="Stripe",
                    mail_template="emails/stripe_connected.html",
                    users=[user],
                )
        return super().retrieve(request, *args, **kwargs)

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
        return UserLocationStorage.get_user_location(user_id=self.get_user_id())

    def retrieve(self, request, *args, **kwargs):
        location_instance, lookup_radius, is_undefined = UserLocationStorage.get_user_location(
            user_id=self.get_user_id()
        )
        serializer = self.get_serializer(
            location_instance,
            context={"lookup_radius": lookup_radius, "is_undefined": is_undefined},
        )
        return Response(serializer.data)


class SetLocationAPIView(AnonymousUserIdAPIMixin, GenericAPIView):
    """
    Set a location for the user when user explicitly provided it
    """

    serializer_class = serializers.SetLocationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            city_location_instance = LocationCity.objects.get(
                slug=serializer.validated_data["slug"]
            )
        except LocationCity.DoesNotExist:
            raise Http404
        UserLocationStorage.set_user_location(
            user_id=self.get_user_id(),
            city_location=city_location_instance,
            lookup_radius=serializer.validated_data["lookup_radius"],
            is_undefined=False,
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


class ConnectStripeCreateAPIView(APIView):
    """
    Create Stripe connection with user account
    """

    permission_classes = (IsAuthenticated, IsVerifiedSeller)

    def create_stripe_account(self, request):
        account = stripe.Account.create(
            type=settings.STRIPE_SELLERS_ACCOUNT_TYPE,
            email=request.user.email,
            metadata={"user.id": request.user.id},
        )
        try:
            user_stripe_connection_model = models.UserStripeConnection.objects.create(
                user=request.user, stripe_account=account.stripe_id
            )
        except IntegrityError:
            models.UserStripeConnection.objects.filter(user=request.user).delete()
            user_stripe_connection_model = models.UserStripeConnection.objects.create(
                user=request.user, stripe_account=account.stripe_id
            )
        return account, user_stripe_connection_model

    def get(self, request, *args, **kwargs):
        connect_link = None
        try:
            user_stripe_connection_model = models.UserStripeConnection.objects.get(
                user=request.user,
            )
        except models.UserStripeConnection.DoesNotExist:
            account, user_stripe_connection_model = self.create_stripe_account(request)
        try:
            connect_link = stripe.AccountLink.create(
                account=user_stripe_connection_model.stripe_account,
                refresh_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_REFRESH_URL}",
                return_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_RETURN_URL}",
                type="account_onboarding",
            )
        except stripe.error.InvalidRequestError as e:
            if "No such account" in e.user_message:
                account, user_stripe_connection_model = self.create_stripe_account(request)
                connect_link = stripe.AccountLink.create(
                    account=user_stripe_connection_model.stripe_account,
                    refresh_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_REFRESH_URL}",
                    return_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_RETURN_URL}",
                    type="account_onboarding",
                )
        if connect_link is None:
            raise ConnectionError("There is no connection link")
        return redirect(connect_link.url)
