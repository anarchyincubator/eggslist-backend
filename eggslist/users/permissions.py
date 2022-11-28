from rest_framework.permissions import BasePermission


class IsVerifiedSeller(BasePermission):
    """
    Checks if user is verified seller
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_verified_seller)
