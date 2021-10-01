from rest_framework import permissions


class UserPostAccessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user

        post_id = obj.id

        user_approved_post_qs = user.approved_user.all()

        if user_approved_post_qs.filter(id=post_id).exists():
            return True
        else:
            return False
