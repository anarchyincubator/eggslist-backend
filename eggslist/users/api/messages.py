from django.utils.translation import gettext_lazy as _

EMAIL_ALREADY_EXISTS = _(
    "User with this email already exists in the databse. "
    "Please, try to login or reset your password."
)

EMAIL_NOT_FOUND = _("User with such an email was not found in the database.")
RESET_CODE_NOT_FOUND = _("Reset code does not exist or expired. Please try again lateri.")
INVALID_CREDENTIALS = _("Invalid Credentials.")
