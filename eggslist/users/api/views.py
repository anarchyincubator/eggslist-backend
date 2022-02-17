from django.contrib.auth import authenticate, get_user_model, login, logout

from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers

User = get_user_model()


class SignInAPIView(GenericAPIView):
    serializer_class = serializers.AuthSerializer
    permission_classes = (~IsAuthenticated,)

    @staticmethod
    def login(request, username, password):
        user = authenticate(request=request, username=username, password=password)
        if not user:
            raise ValidationError({"message": "Invalid credentials"})

        login(request=request, user=user)
        return user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.login(request=request, **serializer.validated_data)
        return Response(status=200)
