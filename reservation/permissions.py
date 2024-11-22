from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        # Example condition for manager permission
        return request.user and request.user.is_staff

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        # Example condition for delivery crew permission
        return request.user and request.user.groups.filter(name='DeliveryCrew').exists()
