from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "users"

# fmt: off
urlpatterns = [
    path("sign-up", views.SignUpAPIView.as_view(), name="sign-up"),
    path("token/obtain", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("current", views.UserProfileAPIView.as_view(), name="current"),
    path("password-change", views.PasswordChangeAPIView.as_view(), name="password-change"),
    path("password-reset-request", views.PasswordResetRequest.as_view(), name="password-reset-request"),
    path("password-reset-confirm", views.PasswordResetConfirm.as_view(), name="password-reset-confirm"),
    path("email-verify-request", views.EmailVerifyRequestAPIView.as_view(), name="email-verify-request"),
    path("email-verify-confirm", views.EmailVerifyConfirmAPIView.as_view(), name="email-verify-confirm"),
    path("locate", views.LocationAPIView.as_view(), name="locate"),
    path("set-location", views.SetLocationAPIView.as_view(), name="set-location"),
]
# fmt: on
