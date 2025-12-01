from rest_framework import permissions
from .models import UserGroup

class IsAdminOrMemberGroup(permissions.BasePermission):
    """
    Admin può fare tutto.
    User può modificare solo se è membro del gruppo.
    Altri possono solo visualizzare.
    """
    def has_permission(self, request, view):
        # Tutti gli utenti autenticati possono vedere
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Per azioni custom come 'join' e 'leave', permettiamo a tutti gli utenti autenticati
        if hasattr(view, 'action') and view.action in ['join', 'leave']:
            return request.user and request.user.is_authenticated
        
        # Per create, tutti gli autenticati possono creare un gruppo
        if hasattr(view, 'action') and view.action == 'create':
            return request.user and request.user.is_authenticated
        
        # Per update/delete serve essere admin o membro del gruppo (controllo in has_object_permission)
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin può fare tutto
        if request.user.is_staff:
            return True
        
        # Tutti possono vedere
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permetti join e leave a tutti
        if hasattr(view, 'action') and view.action in ['join', 'leave']:
            return True
        
        # Per GroupProject: l'utente può modificare solo se è membro del gruppo
        if obj.__class__.__name__ == 'GroupProject':
            return UserGroup.objects.filter(user=request.user, group=obj).exists()
        
        # Per GroupGoal: l'utente può modificare solo se è membro del gruppo
        if hasattr(obj, 'group'):
            return UserGroup.objects.filter(user=request.user, group=obj.group).exists()
        
        return False

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin può fare tutto, altri solo visualizzare.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff