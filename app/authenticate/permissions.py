from rest_framework import permissions


class IsCompanyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsCompanyMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == 'create':
            company_id = request.data.get('company')
            if company_id:
                from .models import Company
                try:
                    company = Company.objects.get(id=company_id)
                    return company.owner == request.user
                except Company.DoesNotExist:
                    return False

        return True

    def has_object_permission(self, request, view, obj):
        return request.user in obj.company.employees.all() or obj.company.owner == request.user


class IsAuthenticatedOrReadOnlyForCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated