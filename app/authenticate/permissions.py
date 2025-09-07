from rest_framework import permissions


class IsCompanyOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'owned_company')

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'company'):
            company = obj.company
        elif hasattr(obj, 'employees'):
            company = obj
        else:
            return False

        return hasattr(request.user, 'owned_company') and request.user.owned_company == company


class IsCompanyMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if hasattr(request.user, 'employee_profile'):
            return request.user.employee_profile.is_active

        if hasattr(request.user, 'owned_company'):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'company'):
            company = obj.company
        elif hasattr(obj, 'employees'):
            company = obj
        else:
            return False

        if hasattr(request.user, 'employee_profile'):
            return request.user.employee_profile.company == company and request.user.employee_profile.is_active

        if hasattr(request.user, 'owned_company'):
            return request.user.owned_company == company

        return False


class IsAuthenticatedOrReadOnlyForCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated