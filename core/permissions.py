from rest_framework import permissions

class IsAdminOrOwnerGroup(permissions.BasePermission):
    """
    Admin può fare tutto.
    User può modificare solo il suo gruppo.
    Altri possono solo visualizzare.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and (request.user.is_staff or request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Per Group: lo user può modificare solo il suo gruppo
        if obj.__class__.__name__ == 'Group':
            return obj.members.filter(id=request.user.id).exists()
        
        # Per GroupGoals: lo user può modificare solo i goal del suo gruppo
        if hasattr(obj, 'group') and request.user.group:
            return obj.group == request.user.group
        
        return False

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin può fare tutto, altri solo visualizzare.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff