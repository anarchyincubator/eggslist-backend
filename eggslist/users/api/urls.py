from django.urls import path

from . import views

app_name = "users"


# fmt: off
urlpatterns = [
    path("sign-up", views.SignUpAPIView.as_view(), name="sign-up"),
    path("sign-in", views.JWTSignInAPIView.as_view(), name="sign-in"),
    path("profile", views.UserProfileAPIView.as_view(), name="current"),
    path("profile/<int:pk>", views.OtherUserProfileAPIView.as_view(), name="other-user-profile"),
    path("profile/update-user-location", views.UserProfileLocationAPIView.as_view(), name="update-user-location"),
    path("password-change", views.PasswordChangeAPIView.as_view(), name="password-change"),
    path("password-reset-request", views.PasswordResetRequest.as_view(), name="password-reset-request"),
    path("password-reset-confirm", views.PasswordResetConfirm.as_view(), name="password-reset-confirm"),
    path("email-verify-request", views.EmailVerifyRequestAPIView.as_view(), name="email-verify-request"),
    path("email-verify-confirm", views.EmailVerifyConfirmAPIView.as_view(), name="email-verify-confirm"),
    path("locate", views.LocationAPIView.as_view(), name="locate"),
    path("set-location", views.SetLocationAPIView.as_view(), name="set-location"),
    path("become-verified-seller", views.BecomeVerifiedSellerAPIView.as_view(), name="become-verified-seller"),
]
# fmt: on
