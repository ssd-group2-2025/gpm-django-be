from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Group, User, Topic, Goal, GroupGoals
from .serializers import (
    GroupSerializer, UserSerializer, TopicSerializer, 
    GoalSerializer, GroupGoalsSerializer
)
from .permissions import IsAdminOrOwnerGroup, IsAdminOrReadOnly


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


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    def get_permissions(self):
        """
        - list/retrieve: tutti gli autenticati
        - create: solo admin
        - update/partial_update/destroy: admin o owner del gruppo
        - join: tutti gli autenticati
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrOwnerGroup()]
        elif self.action == 'join':
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Permetti a un utente di unirsi a un gruppo"""
        group = self.get_object()
        user = request.user
        
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
    queryset = GroupGoals.objects.all()
    serializer_class = GroupGoalsSerializer
    
    def get_permissions(self):
        """Solo admin può creare/modificare/eliminare, tutti possono visualizzare"""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        """Escludi i superuser dalla lista"""
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_superuser=False)
        return queryset
    
    def get_permissions(self):
        """Admin può modificare, tutti possono visualizzare"""
        if self.action in ['list', 'retrieve', 'me']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Ritorna i dati dell'utente corrente"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)