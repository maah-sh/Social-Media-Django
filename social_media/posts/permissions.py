from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrReadOnlyPublished(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user

        is_read_only_published = (
                request.method in permissions.SAFE_METHODS and obj.published
        )

        return is_owner or is_read_only_published