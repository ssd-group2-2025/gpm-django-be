from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Group, User, Topic, Goal, GroupGoals
from .serializers import (
    GroupSerializer, UserSerializer, TopicSerializer, 
    GoalSerializer, GroupGoalsSerializer
)
from .permissions import IsAdminOrOwnerGroup, IsAdminOrReadOnly


class TopicViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class GoalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrOwnerGroup]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Permetti a un utente di unirsi a un gruppo"""
        group = self.get_object()
        user = request.user
        
        # Verifica se l'utente è già in un gruppo
        if user.group:
            return Response(
                {'error': 'Sei già membro di un gruppo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.group = group
        user.save()
        
        return Response(
            {'status': 'Sei entrato nel gruppo', 'group': GroupSerializer(group).data},
            status=status.HTTP_200_OK
        )


class GroupGoalsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrOwnerGroup]
    queryset = GroupGoals.objects.all()
    serializer_class = GroupGoalsSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff and hasattr(self.request.user, 'group') and self.request.user.group:
            queryset = queryset.filter(group=self.request.user.group)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer