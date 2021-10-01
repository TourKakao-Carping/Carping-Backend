from rest_framework import permissions


class UserPostAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return super().has_permission(request, view)
