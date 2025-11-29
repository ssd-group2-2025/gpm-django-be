from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.serializers import ModelSerializer, CharField
from .models import Group

class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UserRegisterSerializer(RegisterSerializer):
    # declare fields you want accepted
    first_name = CharField(required=True, min_length=1, max_length=100)
    last_name = CharField(required=True, min_length=1, max_length=100)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        return data

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()
        return user
