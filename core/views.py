from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Group
from .serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser | IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer