
import pytest
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError

def test_user_creation(db):
    """Test che un utente venga creato correttamente"""
    user = mixer.blend('users.User', matricola='123456')
    assert user.pk is not None
    assert user.email is not None
    assert user.matricola == '123456'


def test_user_matricola_must_be_6_digits(db):
    """Test che la matricola debba avere esattamente 6 cifre"""
    user = mixer.blend('users.User', matricola='12345')
    with pytest.raises(ValidationError) as err:
        user.full_clean()
    assert 'La matricola deve avere 6 cifre numeriche' in str(err.value)


def test_user_matricola_must_be_numeric(db):
    """Test che la matricola debba essere numerica"""
    user = mixer.blend('users.User', matricola='abcdef')
    with pytest.raises(ValidationError) as err:
        user.full_clean()
    assert 'La matricola deve avere 6 cifre numeriche' in str(err.value)


def test_user_matricola_must_be_unique(db):
    """Test che la matricola debba essere unica"""
    mixer.blend('users.User', matricola='123456')
    with pytest.raises(Exception):
        mixer.blend('users.User', matricola='123456')

