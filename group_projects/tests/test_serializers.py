import pytest
from group_projects.models import GroupGoal, GroupProject, Topic, Goal, UserGroup
from group_projects.serializers import GroupGoalsSerializer, GroupProjectSerializer, TopicSerializer, GoalSerializer, UserGroupSerializer
from users.models import User

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

@pytest.mark.django_db
def test_valid_group_project_serializer():
    topic = Topic.objects.create(title="Topic")

    data = {
        "name": "My Project",
        "link_django": "https://example.com/dj",
        "link_tui": "https://example.com/tui",
        "link_gui": "https://example.com/gui",
        "topic": topic.id
    }

    serializer = GroupProjectSerializer(data=data)
    assert serializer.is_valid() and not serializer.errors

    project: GroupProject = serializer.save()
    assert project.name == data["name"]
    assert project.link_django == data["link_django"]
    assert project.link_tui == data["link_tui"]
    assert project.link_gui == data["link_gui"]
    assert project.topic.id == data["topic"]

@pytest.mark.django_db
def test_invalid_links_group_project_serializer():
    topic = Topic.objects.create(title="Topic")

    data = {
        "name": "My Project",
        "link_django": "https://127.0.0.1/dj",
        "link_tui": "https://localhost/tui",
        "link_gui": "http://example.com/gui",
        "topic": topic.id
    }

    serializer = GroupProjectSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 3
    
    assert serializer.errors['link_django'][0].code == 'invalid'
    assert serializer.errors['link_tui'][0].code == 'invalid'
    assert serializer.errors['link_gui'][0].code == 'invalid'

@pytest.mark.django_db
def test_name_too_long_group_project_serializer():
    topic = Topic.objects.create(title="Topic")

    data = {
        "name": "A"*101,
        "link_django": "https://example.com/dj",
        "link_tui": "https://example.com/tui",
        "link_gui": "https://example.com/gui",
        "topic": topic.id
    }

    serializer = GroupProjectSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['name'][0].code == 'max_length'

@pytest.mark.django_db
def test_null_topic_group_project_serializer():
    data = {
        "name": "My Project",
        "link_django": "https://example.com/dj",
        "link_tui": "https://example.com/tui",
        "link_gui": "https://example.com/gui",
        "topic": None
    }

    serializer = GroupProjectSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['topic'][0].code == 'null'

@pytest.mark.django_db
def test_valid_group_goals_serializer():
    topic = Topic.objects.create(title="Topic")
    example_link = 'https://example.org'
    group = GroupProject.objects.create(name='My Group', link_django=example_link, link_tui=example_link, link_gui=example_link, topic=topic)
    goal = Goal.objects.create(title="My Goal", description="Mock Description", points=3)
    
    data = {
        "group": group.id,
        "goal": goal.id,
        "complete": False
    }
    
    serializer = GroupGoalsSerializer(data=data)
    assert serializer.is_valid() and len(serializer.errors) == 0
    
    group_goal: GroupGoal = serializer.save()
    assert group_goal.group.id == group.id
    assert group_goal.goal.id == goal.id
    assert group_goal.complete == data['complete']

@pytest.mark.django_db
def test_null_group_in_group_goals_serializer():
    goal = Goal.objects.create(title="My Goal", description="Mock Description", points=3)
    
    data = {
        "group": None,
        "goal": goal.id,
        "complete": False
    }
    
    serializer = GroupGoalsSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['group'][0].code == 'null'

@pytest.mark.django_db
def test_null_goal_group_goals_serializer():
    topic = Topic.objects.create(title="Topic")
    example_link = 'https://example.org'
    group = GroupProject.objects.create(name='My Group', link_django=example_link, link_tui=example_link, link_gui=example_link, topic=topic)
    
    data = {
        "group": group.id,
        "goal": None,
        "complete": False
    }
    
    serializer = GroupGoalsSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['goal'][0].code == 'null'

@pytest.mark.django_db
def test_valid_user_group_serializer():
    user = User.objects.create(username="testuser")
    topic = Topic.objects.create(title="Topic")
    example_link = 'https://example.org'
    group = GroupProject.objects.create(name='My Group', link_django=example_link, link_tui=example_link, link_gui=example_link, topic=topic)

    data = {
        "user": user.id,
        "group": group.id
    }

    serializer = UserGroupSerializer(data=data)
    assert serializer.is_valid() and len(serializer.errors) == 0

    ug: UserGroup = serializer.save()
    assert ug.user.id == data["user"]
    assert ug.group.id == data["group"]
    
@pytest.mark.django_db
def test_null_user_in_user_group_serializer():
    topic = Topic.objects.create(title="Topic")
    example_link = 'https://example.org'
    group = GroupProject.objects.create(name='My Group', link_django=example_link, link_tui=example_link, link_gui=example_link, topic=topic)

    data = {
        "user": None,
        "group": group.id
    }

    serializer = UserGroupSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['user'][0].code == 'null'

@pytest.mark.django_db
def test_null_group_in_user_group_serializer():
    user = User.objects.create(username="testuser")
    
    data = {
        "user": user.id,
        "group": None
    }

    serializer = UserGroupSerializer(data=data)
    assert not serializer.is_valid() and len(serializer.errors) == 1
    assert serializer.errors['group'][0].code == 'null'