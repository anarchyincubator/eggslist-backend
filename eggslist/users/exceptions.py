from rest_framework.exceptions import ValidationError


class UserException(Exception):
    pass


class ResetCodeDoesNotExist(UserException):
    pass