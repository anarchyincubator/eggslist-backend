from django.urls import path
from . import views

app_name = "users"

# fmt: off
urlpatterns = [
    path("sign-in", views.SignInAPIView.as_view(), name="sign-in"),
]
# fmt: on
