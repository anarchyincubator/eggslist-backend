import typing as t

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.users.determine_location import locate_ip
from eggslist.users.password_reset_storage import PasswordResetStorage
from eggslist.utils.emailing import send_mailing
from . import messages, serializers

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


class LocationAPIView(GenericAPIView):
    serializer_class = serializers.UserLocationSerializer

    def post(self, request: "HttpRequest", *args, **kwargs):
        ip_address = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
        user_location = locate_ip(ip_address)
        if user_location is None:
            data = {"city": None, "state": None, "country": None}
        else:
            serializer = self.get_serializer(instance=user_location)
            data = serializer.data

        return Response(status=200, data=data)
