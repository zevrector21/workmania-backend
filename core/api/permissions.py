from rest_framework import permissions

from core.constants import ORGANIZATION_ADMIN_ROLE_NAME


class CustomPermission(permissions.BasePermission):

    def __init__(self, permission_map):
        super().__init__()
        self.permission_map = permission_map

    def has_permission(self, request, view):
        if (
            hasattr(request.user, 'profile')
            and request.user.profile.role == ORGANIZATION_ADMIN_ROLE_NAME
        ):
            return True

        permissions = self.permission_map.get(request.method, [])
        user_permissions = request.user.get_all_permissions()
        user_permissions = [perm.split('.')[1] for perm in user_permissions]

        return set(permissions).intersection(set(user_permissions))
