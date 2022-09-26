from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()


class EggslistAuthenticationBackend(ModelBackend):
    """
    Allow authentication using both username and email
    """

    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        if (username is None and email is None) or password is None:
            return
        try:
            user = UserModel.objects.get(Q(username=username) | Q(email__in=[email, username]))
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
