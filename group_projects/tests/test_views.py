import pytest
from rest_framework.test import APIRequestFactory
from group_projects.models import Goal, Topic
from group_projects.views import GoalViewSet, TopicViewSet
from rest_framework.response import Response
from users.models import User

@pytest.fixture
def user():
    return User.objects.create_user(username="user", password="pass")

@pytest.fixture
def topic():
    return Topic.objects.create(title="Mock Topic")

@pytest.fixture
def admin():
    return User.objects.create_superuser(username="admin", password="pass")

@pytest.fixture
def goal():
    return Goal.objects.create(title='Mock Goal', description='This is a test goal', points=3)

@pytest.mark.django_db
def test_topic_list_authenticated(user):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"get": "list"})
    req = factory.get("/api/v1/topics/")
    req.user = user

    res = view(req)

    assert res.status_code == 200

@pytest.mark.django_db
def test_topic_list_unauthenticated():
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"get": "list"})
    req = factory.get("/api/v1/topics/")
    req.user = None

    res: Response = view(req)
    
    assert res.status_code == 401
    assert res.data['detail'].code == 'not_authenticated'

@pytest.mark.django_db
def test_topic_retrieve_authenticated(user, topic):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"get": "retrieve"})
    req = factory.get("/api/v1/topics/1")
    req.user = user

    res = view(req, pk=topic.id)
    assert res.status_code == 200
    assert res.data["id"] == topic.id

@pytest.mark.django_db
def test_topic_create_forbidden_for_non_admin(user):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"post": "create"})
    req = factory.post("/api/v1/topics/", {"name": "New"})
    req.user = user

    res: Response = view(req)
    assert res.status_code == 403
    assert res.data['detail'].code == 'permission_denied'

@pytest.mark.django_db
def test_topic_create_admin(admin):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"post": "create"})
    req = factory.post("/api/v1/topics/", {"title": "Admin Topic"}, format="json")
    req.user = admin

    res = view(req)

    assert res.status_code == 201
    assert Topic.objects.filter(title="Admin Topic").exists()

@pytest.mark.django_db
def test_topic_update_forbidden_for_non_admin(user, topic):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"put": "update"})
    req = factory.put("/api/v1/topics/1/", {"name": "Changed"})
    req.user = user

    res = view(req, pk=topic.id)

    assert res.status_code == 403
    assert res.data['detail'].code == 'permission_denied'

@pytest.mark.django_db
def test_topic_update_admin(admin, topic):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"put": "update"})
    req = factory.put("/api/v1/topics/1/", {"title": "Changed Admin"}, format="json")
    req.user = admin

    res = view(req, pk=topic.id)

    assert res.status_code == 200
    topic.refresh_from_db()
    assert topic.title == "Changed Admin"

@pytest.mark.django_db
def test_topic_destroy_forbidden_for_non_admin(user, topic):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"delete": "destroy"})
    req = factory.delete("/api/v1/topics/1/")
    req.user = user

    res = view(req, pk=topic.id)

    assert res.status_code == 403
    assert res.data['detail'].code == 'permission_denied'
    
@pytest.mark.django_db
def test_topic_destroy_admin(admin, topic):
    factory = APIRequestFactory()
    view = TopicViewSet.as_view({"delete": "destroy"})
    req = factory.delete("/topics/1/")
    req.user = admin

    res = view(req, pk=topic.id)

    assert res.status_code == 204
    assert not Topic.objects.filter(id=topic.id).exists()

@pytest.mark.django_db
def test_goal_list_authenticated(user):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"get": "list"})
    req = factory.get("/api/v1/goals/")
    req.user = user

    res = view(req)
    assert res.status_code == 200

@pytest.mark.django_db
def test_goal_retrieve_authenticated(user, goal):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"get": "retrieve"})
    req = factory.get(f"/api/v1/goals/{goal.id}")
    req.user = user

    res = view(req, pk=goal.id)
    assert res.status_code == 200
    assert res.data["id"] == goal.id
    
@pytest.mark.django_db
def test_goal_create_forbidden_for_non_admin(user):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"post": "create"})
    req = factory.post("/api/v1/goals/", {"title": "New"}, format="json")
    req.user = user

    res: Response = view(req)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_goal_create_admin(admin):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"post": "create"})
    req = factory.post("/api/v1/goals/", {"title": "Admin Goal", "description": "Desc", "points": 3}, format="json")
    req.user = admin

    res = view(req)
    assert res.status_code == 201
    assert Goal.objects.filter(title="Admin Goal").exists()

@pytest.mark.django_db
def test_goal_update_forbidden_for_non_admin(user, goal):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"put": "update"})
    req = factory.put(f"/api/v1/goals/{goal.id}/", {"title": "Changed"}, format="json")
    req.user = user

    res = view(req, pk=goal.id)

    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_goal_update_admin(admin, goal):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"put": "update"})
    req = factory.put(f"/api/v1/goals/{goal.id}/", {"title": "Changed Admin", "description": goal.description, "points": goal.points}, format="json")
    req.user = admin

    res = view(req, pk=goal.id)
    assert res.status_code == 200
    goal.refresh_from_db()
    assert goal.title == "Changed Admin"

@pytest.mark.django_db
def test_goal_destroy_forbidden_for_non_admin(user, goal):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"delete": "destroy"})
    req = factory.delete(f"/api/v1/goals/{goal.id}/")
    req.user = user

    res: Response = view(req, pk=goal.id)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_goal_destroy_admin(admin, goal):
    factory = APIRequestFactory()
    view = GoalViewSet.as_view({"delete": "destroy"})
    req = factory.delete(f"/api/v1/goals/{goal.id}/")
    req.user = admin

    res = view(req, pk=goal.id)
    assert res.status_code == 204
    assert not Goal.objects.filter(id=goal.id).exists()