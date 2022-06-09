from django.urls import path

from . import views

app_name = "users"

# fmt: off
urlpatterns = [
    path("sign-in", views.SignInAPIView.as_view(), name="sign-in"),
    path("sign-up", views.SignUpAPIView.as_view(), name="sign-up"),
    path("sign-out", views.SignOutAPIView.as_view(), name="sign-out"),
    path("current", views.UserProfileAPIView.as_view(), name="current"),
    path("password-change", views.PasswordChangeAPIView.as_view(), name="password-change"),
    path("password-reset-request", views.PasswordResetRequest.as_view(), name="password-reset-request"),
    path("password-reset-confirm", views.PasswordResetConfirm.as_view(), name="password-reset-confirm"),
    path("locate", views.LocationAPIView.as_view(), name="locate")
]
# fmt: on
