from rest_framework import viewsets
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