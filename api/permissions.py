# api/permissions.py

from rest_framework import permissions

class IsFarmerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow farmers to edit objects.
    Read-only access for everyone else (e.g., buyers).
    """
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return True
       
        return request.user.user_type == 'FARMER'

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        owner = getattr(obj, 'buyer', getattr(obj, 'user', None))
        return owner == request.user or request.user.is_staff