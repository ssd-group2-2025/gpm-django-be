import pytest
from group_projects.models import Topic, Goal
from group_projects.serializers import TopicSerializer, GoalSerializer

@pytest.mark.django_db
def test_valid_topic_serializer():
    data = {
        'title': 'TestTitle'
    }
    
    serializer = TopicSerializer(data=data)
    
    assert serializer.is_valid() and len(serializer.errors) == 0
    topic: Topic = serializer.save()
    
    assert topic.title == data['title']

@pytest.mark.django_db
def test_invalid_topic_serializer():
    data = {
        'title': 'A'*150
    }
    
    serializer = TopicSerializer(data=data)
    assert not serializer.is_valid()
    errors = serializer.errors
    assert errors.get('title') is not None and len(errors.get('title')) == 1
    title_error = errors['title'][0]
    assert title_error.code == 'max_length'

@pytest.mark.django_db
def test_valid_goals_serializer():
    data = {
        'title': 'Test Title',
        'description': 'This a mock description!',
        'points': 3
    }
    
    serializer = GoalSerializer(data=data)
    assert serializer.is_valid() and len(serializer.errors) == 0
    
    goal: Goal = serializer.save()
    assert goal.title == data['title']
    assert goal.description == data['description']
    assert goal.points == data['points']

@pytest.mark.django_db
def test_title_too_long_goals_serializer():
    data = {
        'title': 'A'*101,
        'description': 'This is a mock description!',
        'points': 3
    }
    
    serializer = GoalSerializer(data=data)
    assert not serializer.is_valid() and serializer.errors.get('title') is not None
    assert len(serializer.errors.get('title')) == 1
    title_error = serializer.errors['title'][0]
    assert title_error.code == 'max_length'

@pytest.mark.django_db
def test_desc_too_long_goals_serializer():
    data = {
        'title': 'Test Title',
        'description': 'A'*401,
        'points': 3
    }
    
    serializer = GoalSerializer(data=data)
    assert not serializer.is_valid() and serializer.errors.get('description') is not None
    assert len(serializer.errors.get('description')) == 1
    desc_error = serializer.errors['description'][0]
    assert desc_error.code == 'max_length'

@pytest.mark.django_db
def test_min_value_points_goals_serializer():
    data = {
        'title': 'Test Title',
        'description': 'mock description',
        'points': -1
    }
    
    serializer = GoalSerializer(data=data)
    assert not serializer.is_valid() and serializer.errors.get('points') is not None
    assert len(serializer.errors.get('points')) == 1
    points_error = serializer.errors['points'][0]
    assert points_error.code == 'min_value'


@pytest.mark.django_db
def test_max_value_points_goals_serializer():
    data = {
        'title': 'Test Title',
        'description': 'mock description',
        'points': 10
    }
    
    serializer = GoalSerializer(data=data)
    assert not serializer.is_valid() and serializer.errors.get('points') is not None
    assert len(serializer.errors.get('points')) == 1
    points_error = serializer.errors['points'][0]
    assert points_error.code == 'max_value'