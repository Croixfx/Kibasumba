"""Role-based DRF permission classes, used heavily from Sprint 4 onward."""
from rest_framework.permissions import BasePermission


def _has_role(request, roles):
    user = request.user
    return bool(user and user.is_authenticated and user.role in roles)


class IsWoman(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, ["woman"])


class IsMidwife(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, ["midwife", "admin"])


class IsCHW(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, ["chw", "midwife", "admin"])


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, ["admin"])


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request, ["midwife", "chw", "admin"])
