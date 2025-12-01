from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import GroupProject, Topic, Goal, GroupGoal, UserGroup
from .serializers import (
    GroupProjectSerializer, TopicSerializer, 
    GoalSerializer, GroupGoalsSerializer, UserGroupSerializer
)
from .permissions import IsAdminOrMemberGroup


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    
    def get_permissions(self):
        """Admin può modificare, tutti possono visualizzare"""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    
    def get_permissions(self):
        """Admin può modificare, tutti possono visualizzare"""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]


class GroupProjectViewSet(viewsets.ModelViewSet):
    queryset = GroupProject.objects.all()
    serializer_class = GroupProjectSerializer
    
    def get_permissions(self):
        """
        - list/retrieve: tutti gli autenticati
        - create: tutti gli autenticati
        - update/partial_update/destroy: admin o owner del gruppo
        - join/leave: tutti gli autenticati
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated()]  
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrMemberGroup()]
        elif self.action in ['join', 'leave']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Permetti a un utente di unirsi a un gruppo"""
        group = self.get_object()
        user = request.user
        
        if 'user_id' in request.data and request.data['user_id'] != user.id:
            return Response(
                {'error': 'Puoi aggiungere solo te stesso a un gruppo'}, 
                status=status.HTTP_403_FORBIDDEN
            )
 
        if UserGroup.objects.filter(user=user, group=group).exists():
            return Response(
                {'error': 'Sei già membro di questo gruppo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        UserGroup.objects.create(user=user, group=group)
        
        return Response(
            {'status': 'Sei entrato nel gruppo', 'group': GroupProjectSerializer(group).data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['delete'])
    def leave(self, request, pk=None):
        """Permetti a un utente di lasciare un gruppo"""
        group = self.get_object()
        user = request.user
        
        try:
            user_group = UserGroup.objects.get(user=user, group=group)
        except UserGroup.DoesNotExist:
            return Response(
                {'error': 'Non sei membro di questo gruppo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_group.delete()
        
        return Response(
            {'status': 'Hai lasciato il gruppo'},
            status=status.HTTP_200_OK
        )


class GroupGoalViewSet(viewsets.ModelViewSet):
    queryset = GroupGoal.objects.all()
    serializer_class = GroupGoalsSerializer
    
    def get_permissions(self):
        """Solo admin può creare/modificare/eliminare, tutti possono visualizzare"""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]


class UserGroupViewset(viewsets.ModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer
    
    def get_permissions(self):
        """
        - list/retrieve: tutti gli autenticati
        - create/update/partial_update: solo admin
        - destroy: solo admin
        - leave: l'utente può rimuovere solo se stesso
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]
    
