from rest_framework import permissions

class IsCompanyAdmin(permissions.BasePermission):
    """
    User level permission to allow only company admin
    to update or delete their company.
    """
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.company_role == 'AD':
            return True
        return False