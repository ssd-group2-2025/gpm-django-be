from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.serializers import ModelSerializer, CharField
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
from .models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'matricola']

class UserRegisterSerializer(RegisterSerializer):
    first_name = CharField(required=True, min_length=1, max_length=100)
    last_name = CharField(required=True, min_length=1, max_length=100)
    matricola = CharField(required=True, validators = [
        RegexValidator(r'^\d{6}$', "La matricola deve avere 6 cifre numeriche"),
        UniqueValidator(queryset=User.objects.all(), message="Questa matricola è già utilizzata.")
    ])

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        data['matricola'] = self.validated_data.get('matricola', '')
        return data

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.matricola = self.validated_data.get('matricola', '')
        user.save()
        return user