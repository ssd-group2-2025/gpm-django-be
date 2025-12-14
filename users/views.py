from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import CustomTokenObtainPairSerializer
from django.conf import settings


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Prendi solo il refresh token dalla risposta
            refresh_token = response.data.get('refresh')
            
            # Imposta SOLO il refresh token come cookie HttpOnly
            # L'access token rimane nel body della risposta per il frontend
            if refresh_token:
                response.set_cookie(
                    key=settings.REST_AUTH.get('JWT_AUTH_REFRESH_COOKIE', 'jwt-refresh'),
                    value=refresh_token,
                    httponly=True,
                    secure=False,  # True in produzione con HTTPS
                    samesite='Lax',
                )
        
        return response


class CustomLogoutView(APIView):
    permission_classes = [AllowAny]  # Non serve autenticazione, basta il refresh token
    
    def post(self, request):
        # Prova a leggere il refresh token dai cookie
        refresh_token = request.COOKIES.get(settings.REST_AUTH.get('JWT_AUTH_REFRESH_COOKIE', 'jwt-refresh'))
        
        if not refresh_token:
            # Se non è nei cookie, prova nel body
            refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {"detail": "Refresh token was not included in cookie data."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Token is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        # Cancella i cookie
        response.delete_cookie(settings.REST_AUTH.get('JWT_AUTH_COOKIE', 'jwt-auth'))
        response.delete_cookie(settings.REST_AUTH.get('JWT_AUTH_REFRESH_COOKIE', 'jwt-refresh'))
        
        return response


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