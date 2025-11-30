import pytest
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
from core.models import User, Topic, Group, Goal, GroupGoals


# ============== USER MODEL TESTS ==============

def test_user_creation(db):
    """Test che un utente venga creato correttamente"""
    user = mixer.blend('core.User', matricola='123456')
    assert user.pk is not None
    assert user.email is not None
    assert user.matricola == '123456'


def test_user_matricola_must_be_6_digits(db):
    """Test che la matricola debba avere esattamente 6 cifre"""
    user = mixer.blend('core.User', matricola='12345')
    with pytest.raises(ValidationError) as err:
        user.full_clean()
    assert 'La matricola deve avere 6 cifre numeriche' in str(err.value)


def test_user_matricola_must_be_numeric(db):
    """Test che la matricola debba essere numerica"""
    user = mixer.blend('core.User', matricola='abcdef')
    with pytest.raises(ValidationError) as err:
        user.full_clean()
    assert 'La matricola deve avere 6 cifre numeriche' in str(err.value)


def test_user_matricola_must_be_unique(db):
    """Test che la matricola debba essere unica"""
    mixer.blend('core.User', matricola='123456')
    with pytest.raises(Exception):
        mixer.blend('core.User', matricola='123456')


def test_user_can_belong_to_group(db):
    """Test che un utente possa appartenere a un gruppo"""
    group = mixer.blend('core.Group')
    user = mixer.blend('core.User', matricola='123456', group=group)
    assert user.group == group
    assert user in group.members.all()


# ============== TOPIC MODEL TESTS ==============

def test_topic_creation(db):
    """Test che un topic venga creato correttamente"""
    topic = mixer.blend('core.Topic', title='Test Topic')
    assert topic.pk is not None
    assert topic.title == 'Test Topic'


def test_topic_title_max_length(db):
    """Test che il titolo del topic non superi 100 caratteri"""
    topic = mixer.blend('core.Topic', title='A' * 101)
    with pytest.raises(ValidationError):
        topic.full_clean()


# ============== GOAL MODEL TESTS ==============

def test_goal_creation(db):
    """Test che un goal venga creato correttamente"""
    goal = mixer.blend('core.Goal', title='Test Goal', points=3)
    assert goal.pk is not None
    assert goal.title == 'Test Goal'
    assert goal.points == 3


def test_goal_points_min_value(db):
    """Test che i punti del goal non siano inferiori a 1"""
    goal = mixer.blend('core.Goal', points=0)
    with pytest.raises(ValidationError) as err:
        goal.full_clean()
    assert 'greater than or equal to 1' in str(err.value)


def test_goal_points_max_value(db):
    """Test che i punti del goal non superino 5"""
    goal = mixer.blend('core.Goal', points=6)
    with pytest.raises(ValidationError) as err:
        goal.full_clean()
    assert 'less than or equal to 5' in str(err.value)


def test_goal_description_max_length(db):
    """Test che la descrizione del goal non superi 400 caratteri"""
    goal = mixer.blend('core.Goal', description='A' * 401)
    with pytest.raises(ValidationError):
        goal.full_clean()


# ============== GROUP MODEL TESTS ==============

def test_group_creation(db):
    """Test che un gruppo venga creato correttamente"""
    topic = mixer.blend('core.Topic')
    group = mixer.blend('core.Group', 
                       name='Test Group',
                       topic=topic,
                       link_django='https://example.com/django',
                       link_tui='https://example.com/tui',
                       link_gui='https://example.com/gui')
    assert group.pk is not None
    assert group.name == 'Test Group'
    assert group.topic == topic


def test_group_link_must_be_https(db):
    """Test che i link del gruppo debbano usare HTTPS"""
    topic = mixer.blend('core.Topic')
    group = mixer.blend('core.Group',
                       topic=topic,
                       link_django='http://example.com')
    with pytest.raises(ValidationError) as err:
        group.full_clean()
    assert 'URL must use HTTPS' in str(err.value)


def test_group_link_cannot_be_localhost(db):
    """Test che i link del gruppo non possano essere localhost"""
    topic = mixer.blend('core.Topic')
    group = mixer.blend('core.Group',
                       topic=topic,
                       link_django='https://localhost:8000')
    with pytest.raises(ValidationError) as err:
        group.full_clean()
    assert 'Localhost URLs are not allowed' in str(err.value)


def test_group_link_cannot_be_ip(db):
    """Test che i link del gruppo non possano essere indirizzi IP"""
    topic = mixer.blend('core.Topic')
    group = mixer.blend('core.Group',
                       topic=topic,
                       link_django='https://192.168.1.1')
    with pytest.raises(ValidationError) as err:
        group.full_clean()
    assert 'IP addresses are not allowed' in str(err.value)


# ============== GROUPGOALS MODEL TESTS ==============

def test_groupgoals_creation(db):
    """Test che una relazione gruppo-goal venga creata correttamente"""
    group = mixer.blend('core.Group')
    goal = mixer.blend('core.Goal')
    group_goal = mixer.blend('core.GroupGoals', group=group, goal=goal, complete=False)
    assert group_goal.pk is not None
    assert group_goal.group == group
    assert group_goal.goal == goal
    assert group_goal.complete is False


def test_groupgoals_complete_default_false(db):
    """Test che il campo complete sia False di default"""
    group_goal = mixer.blend('core.GroupGoals')
    assert group_goal.complete is False


def test_groupgoals_can_be_completed(db):
    """Test che un goal possa essere marcato come completato"""
    group_goal = mixer.blend('core.GroupGoals', complete=True)
    assert group_goal.complete is True