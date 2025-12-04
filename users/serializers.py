from django.forms import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import JWTSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['email'] = user.email
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['matricola'] = user.matricola
        
        return token


class CustomJWTSerializer(JWTSerializer):
    def get_token(self, obj):
        user = obj.get('user') if isinstance(obj, dict) else obj
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'matricola']
        read_only_fields = ['id']


class UserRegisterSerializer(RegisterSerializer):
    matricola = serializers.CharField(max_length=6, min_length=6, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'matricola': self.validated_data.get('matricola', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }
    
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)

        user.matricola = self.cleaned_data.get('matricola')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        try:
            user.full_clean()
        except DjangoValidationError as ex:
            raise ValidationError(ex.message_dict)
        user.save()
        setup_user_email(request, user, [])
        return user