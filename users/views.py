from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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