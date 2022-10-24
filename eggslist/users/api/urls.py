from django.urls import path

from eggslist.utils.social.api import views as social_views
from . import views

app_name = "users"


# fmt: off
urlpatterns = [
    path("sign-up", views.SignUpAPIView.as_view(), name="sign-up"),
    path("sign-in", views.JWTSignInAPIView.as_view(), name="sign-in"),
    path("social/google/sign-in", social_views.GoogleAuthURLAPIView.as_view(), name="google-sign-in"),
    path("social/google/callback", social_views.GoogleAuthCallbackAPIView.as_view(), name="google-callback"),
    path("social/facebook/sign-in", social_views.FacebookAuthURLAPIView.as_view(), name="sign-in-google-callback"),
    path("social/facebook/callback", social_views.FacebookAuthCallbackAPIView.as_view(), name="sign-in-facebook-callback"),
    path("profile", views.UserProfileAPIView.as_view(), name="current"),
    path("profile/<int:pk>", views.OtherUserProfileAPIView.as_view(), name="other-user-profile"),
    path("password-change", views.PasswordChangeAPIView.as_view(), name="password-change"),
    path("password-reset-request", views.PasswordResetRequest.as_view(), name="password-reset-request"),
    path("password-reset-confirm", views.PasswordResetConfirm.as_view(), name="password-reset-confirm"),
    path("email-verify-request", views.EmailVerifyRequestAPIView.as_view(), name="email-verify-request"),
    path("email-verify-confirm", views.EmailVerifyConfirmAPIView.as_view(), name="email-verify-confirm"),
    path("locate", views.LocationAPIView.as_view(), name="locate"),
    path("set-location", views.SetLocationAPIView.as_view(), name="set-location"),
    path("become-verified-seller", views.BecomeVerifiedSellerAPIView.as_view(), name="become-verified-seller"),
    path("<int:following_user>/change-favorite-status", views.ChangeFavoriteStatus.as_view(), name="change-favorite-status"),
    path("profile/favorite-farmers", views.FavoriteUsersListAPIView.as_view(), name="favorite-farmers"),
]
# fmt: on
