from rest_framework import permissions


class UserPostAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        print(view.serializer_class)
        string = request.META['QUERY_STRING']
        print(request.data)
        user = request.user

        return True
