from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from users.serializers import UserSerializer, UserRegisterSerializer
from rest_framework.exceptions import ValidationError
from users.models import User
import pytest

@pytest.fixture
def mock_request():
    factory = RequestFactory()
    request = factory.post("/api/v1/auth/register")
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    yield request

@pytest.mark.django_db
def test_valid_user_serializer():
    data = {
        "email": "mail@example.com",
        "username": "example_user",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456"
    }
    
    serializer = UserSerializer(data=data)
    assert serializer.is_valid() and len(serializer.errors) == 0
    user: User = serializer.save()
    
    assert user.email == data['email']
    assert user.username == data['username']
    assert user.first_name == data['first_name']
    assert user.last_name == data['last_name']
    assert user.matricola == data['matricola']

@pytest.mark.django_db
def test_bad_email_in_user_serializer():
    data = {
        "email": "abc123",
        "username": "example_user",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456"
    }
    
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['email'][0].code == 'invalid'

@pytest.mark.django_db
def test_bad_matricola_in_user_serializer():
    data = {
        "email": "mail@example.com",
        "username": "example_user",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "this is not a valid matricola!"
    }
    
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['matricola'][0].code == 'invalid'

@pytest.mark.django_db
def test_unique_email_in_user_serializer():
    u1_data = {
        "email": "mail@example.com",
        "username": "example_user1",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456"
    }
    
    u1_serializer = UserSerializer(data=u1_data)
    assert u1_serializer.is_valid()
    u1: User = u1_serializer.save()
    
    u2_data = {
        "email": "mail@example.com",
        "username": "example_user2",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "234567"
    }

    u2_serializer = UserSerializer(data=u2_data)
    
    assert not u2_serializer.is_valid() and len(u2_serializer.errors) == 1
    assert u2_serializer.errors['email'][0].code == 'unique'

@pytest.mark.django_db
def test_unique_matricola_in_user_serializer():
    u1_data = {
        "email": "mail1@example.com",
        "username": "example_user1",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456"
    }
    
    u1_serializer = UserSerializer(data=u1_data)
    assert u1_serializer.is_valid()
    u1: User = u1_serializer.save()
    
    u2_data = {
        "email": "mail2@example.com",
        "username": "example_user2",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456"
    }

    u2_serializer = UserSerializer(data=u2_data)
    
    assert not u2_serializer.is_valid() and len(u2_serializer.errors) == 1
    assert u2_serializer.errors['matricola'][0].code == 'unique'

@pytest.mark.django_db
def test_valid_user_register_serializer(mock_request):
    data = {
        "email": "mail@example.com",
        "username": "example_user",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456",
        "password1": "Sup3rSecur3P4ssw0rd!!",
        "password2": "Sup3rSecur3P4ssw0rd!!"
    }
    
    serializer = UserRegisterSerializer(data=data)
    assert serializer.is_valid() and len(serializer.errors) == 0
    
    user: User = serializer.save(mock_request)
    
    assert user.email == data['email']
    assert user.username == data['username']
    assert user.first_name == data['first_name']
    assert user.last_name == data['last_name']
    assert user.matricola == data['matricola']

@pytest.mark.django_db
def test_psw_dont_match_user_register_serializer():
    data = {
        "email": "mail@example.com",
        "username": "example_user",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456",
        "password1": "Sup3rSecur3P4ssw0rd_1",
        "password2": "Sup3rSecur3P4ssw0rd_2"
    }
    
    serializer = UserRegisterSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['non_field_errors'][0].code == 'invalid'

@pytest.mark.django_db
def test_bad_email_in_user_register_serializer():
    data = {
        "email": "this is not a valid email",
        "username": "example_user",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456",
        "password1": "Sup3rSecur3P4ssw0rd!!",
        "password2": "Sup3rSecur3P4ssw0rd!!"
    }
    
    serializer = UserRegisterSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['email'][0].code == 'invalid'

@pytest.mark.django_db
def test_bad_matricola_in_user_register_serializer(mock_request):
    data = {
        "email": "mail@example.com",
        "username": "example_user",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "nvalid",
        "password1": "Sup3rSecur3P4ssw0rd!!",
        "password2": "Sup3rSecur3P4ssw0rd!!"
    }
    
    serializer = UserRegisterSerializer(data=data)
    assert serializer.is_valid() and len(serializer.errors) == 0
    with pytest.raises(ValidationError) as ex:
        serializer.save(mock_request)

    assert 'The matricola must contain exactly 6 digits' in str(ex)

@pytest.mark.django_db
def test_unique_email_in_user_register_serializer(mock_request):
    u1_data = {
        "email": "mail@example.com",
        "username": "example_user1",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456",
        "password1": "Sup3rSecur3P4ssw0rd!!",
        "password2": "Sup3rSecur3P4ssw0rd!!"
    }
    
    u1_serializer = UserRegisterSerializer(data=u1_data)
    assert u1_serializer.is_valid()
    u1_serializer.save(mock_request)
    
    u2_data = {
        "email": "mail@example.com",
        "username": "example_user2",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "234567",
        "password1": "Sup3rSecur3P4ssw0rd!!",
        "password2": "Sup3rSecur3P4ssw0rd!!"
    }
    
    u2_serializer = UserRegisterSerializer(data=u2_data)
    assert u2_serializer.is_valid()
    
    with pytest.raises(ValidationError) as ex:
        u2_serializer.save(mock_request)

    assert 'User with this Email already exists' in str(ex)

@pytest.mark.django_db
def test_unique_matricola_in_user_register_serializer(mock_request):
    u1_data = {
        "email": "mail1@example.com",
        "username": "example_user1",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456",
        "password1": "Sup3rSecur3P4ssw0rd!!",
        "password2": "Sup3rSecur3P4ssw0rd!!"
    }
    
    u1_serializer = UserRegisterSerializer(data=u1_data)
    assert u1_serializer.is_valid()
    u1_serializer.save(mock_request)
    
    u2_data = {
        "email": "mail2@example.com",
        "username": "example_user2",
        "first_name": "Mario",
        "last_name": "Rossi",
        "matricola": "123456",
        "password1": "Sup3rSecur3P4ssw0rd!!",
        "password2": "Sup3rSecur3P4ssw0rd!!"
    }
    
    u2_serializer = UserRegisterSerializer(data=u2_data)
    assert u2_serializer.is_valid()
    
    with pytest.raises(ValidationError) as ex:
        u2_serializer.save(mock_request)

    assert 'User with this Matricola already exists' in str(ex)