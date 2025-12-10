import pytest
from rest_framework.test import APIRequestFactory
from group_projects.models import Goal, GroupGoal, Topic, GroupProject, UserGroup
from group_projects.views import GoalViewSet, TopicViewSet, GroupProjectViewSet, GroupGoalViewSet, UserGroupViewset
from rest_framework.response import Response
from users.models import User
import uuid
import random

@pytest.fixture
def user():
    random_matricola = "".join([ str(random.randint(0, 9)) for _ in range(6) ])
    return User.objects.create_user(username="user", password="pass", email=f"user_{uuid.uuid4().hex}@example.org", matricola=random_matricola)

@pytest.fixture
def topic():
    return Topic.objects.create(title="Mock Topic")

@pytest.fixture
def admin():
    random_matricola = "".join([ str(random.randint(0, 9)) for _ in range(6) ])
    return User.objects.create_superuser(username="admin", password="pass", email=f"admin_{uuid.uuid4().hex}@example.org", matricola=random_matricola)

@pytest.fixture
def goal():
    return Goal.objects.create(title='Mock Goal', description='This is a test goal', points=3)

@pytest.fixture
def group_goal(group, goal):
    return GroupGoal.objects.create(group=group, goal=goal)

@pytest.fixture
def user_group(user, group):
    return UserGroup.objects.create(user=user, group=group)

@pytest.fixture
def group(topic):
    return GroupProject.objects.create(
        name="Test Group",
        topic=topic,
        link_django="https://example.com",
        link_tui="https://example.com",
        link_gui="https://example.com"
    )

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

@pytest.mark.django_db
def test_group_list_unauthenticated(group):
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"get": "list"})
    req = factory.get("/groups/")
    req.user = None

    res: Response = view(req)
    assert res.status_code == 401
    assert res.data["detail"].code == "not_authenticated"
    
@pytest.mark.django_db
def test_group_create_authenticated(user, topic):
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"post": "create"})
    req = factory.post(
        "/groups/",
        {
            "name": "New Group",
            "topic": topic.id,
            "link_django": "https://example.com",
            "link_tui": "https://example.com",
            "link_gui": "https://example.com"
        },
        format="json"
    )
    req.user = user

    res = view(req)
    assert res.status_code == 201
    assert GroupProject.objects.filter(name="New Group").exists()

@pytest.mark.django_db
def test_group_update_requires_admin(admin, user, group):
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"put": "update"})
    req = factory.put(
        f"/groups/{group.id}/",
        {
            "name": "Updated Name",
            "topic": group.topic.id,
            "link_django": group.link_django,
            "link_tui": group.link_tui,
            "link_gui": group.link_gui
        },
        format="json"
    )

    # Non-admin user cannot update
    req.user = user
    res = view(req, pk=group.id)
    assert res.status_code == 403

    # Admin user can update
    req.user = admin
    res = view(req, pk=group.id)
    assert res.status_code == 200
    group.refresh_from_db()
    assert group.name == "Updated Name"

@pytest.mark.django_db
def test_group_destroy_requires_admin(admin, user, group):
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"delete": "destroy"})

    # Non-admin cannot delete
    req = factory.delete(f"/groups/{group.id}/")
    req.user = user
    res = view(req, pk=group.id)
    assert res.status_code == 403

    # Admin can delete
    req = factory.delete(f"/groups/{group.id}/")
    req.user = admin
    res = view(req, pk=group.id)
    assert res.status_code == 204
    assert not GroupProject.objects.filter(id=group.id).exists()

@pytest.mark.django_db
def test_group_join_success(user, group):
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"post": "join"})
    req = factory.post(f"/groups/{group.id}/join/", {})
    req.user = user

    res = view(req, pk=group.id)
    assert res.status_code == 200
    assert UserGroup.objects.filter(user=user, group=group).exists()
    assert res.data["status"] == "Sei entrato nel gruppo"

@pytest.mark.django_db
def test_group_join_twice(user, group):
    UserGroup.objects.create(user=user, group=group)
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"post": "join"})
    req = factory.post(f"/groups/{group.id}/join/", {})
    req.user = user

    res = view(req, pk=group.id)
    assert res.status_code == 400
    assert "già membro" in res.data["error"]

@pytest.mark.django_db
def test_group_join_other_user_id(user, group):
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"post": "join"})
    req = factory.post(f"/groups/{group.id}/join/", {"user_id": 999})
    req.user = user

    res = view(req, pk=group.id)
    assert res.status_code == 403
    assert "Puoi aggiungere solo te stesso" in res.data["error"]

@pytest.mark.django_db
def test_group_leave_success(user, group):
    UserGroup.objects.create(user=user, group=group)
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"delete": "leave"})
    req = factory.delete(f"/groups/{group.id}/leave/")
    req.user = user

    res = view(req, pk=group.id)
    assert res.status_code == 200
    assert not UserGroup.objects.filter(user=user, group=group).exists()
    assert res.data["status"] == "Hai lasciato il gruppo"

@pytest.mark.django_db
def test_group_leave_not_member(user, group):
    factory = APIRequestFactory()
    view = GroupProjectViewSet.as_view({"delete": "leave"})
    req = factory.delete(f"/groups/{group.id}/leave/")
    req.user = user

    res = view(req, pk=group.id)
    assert res.status_code == 400
    assert "Non sei membro" in res.data["error"]

@pytest.mark.django_db
def test_group_goal_list_authenticated(user):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"get": "list"})
    req = factory.get("/group-goals/")
    req.user = user

    res = view(req)
    assert res.status_code == 200

@pytest.mark.django_db
def test_group_goal_list_unauthenticated(group_goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"get": "list"})
    req = factory.get("/group-goals/")
    req.user = None

    res: Response = view(req)
    assert res.status_code == 401
    assert res.data["detail"].code == "not_authenticated"

@pytest.mark.django_db
def test_group_goal_retrieve_authenticated(user, group_goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"get": "retrieve"})
    req = factory.get(f"/group-goals/{group_goal.id}/")
    req.user = user

    res = view(req, pk=group_goal.id)
    assert res.status_code == 200
    assert res.data["id"] == group_goal.id

@pytest.mark.django_db
def test_group_goal_create_forbidden_for_non_admin(user, group, goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"post": "create"})
    req = factory.post("/group-goals/", {"group": group.id, "goal": goal.id, "complete": False})
    req.user = user

    res: Response = view(req)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_group_goal_create_admin(admin, group, goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"post": "create"})
    req = factory.post("/group-goals/", {"group": group.id, "goal": goal.id, "complete": False}, format="json")
    req.user = admin

    res = view(req)
    assert res.status_code == 201
    assert GroupGoal.objects.filter(group=group, goal=goal).exists()

@pytest.mark.django_db
def test_group_goal_update_forbidden_for_non_admin(user, group_goal, group, goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"put": "update"})
    req = factory.put(f"/group-goals/{group_goal.id}/", {"group": group.id, "goal": goal.id, "complete": True}, format="json")
    req.user = user

    res: Response = view(req, pk=group_goal.id)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_group_goal_update_admin(admin, group_goal, group, goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"put": "update"})
    req = factory.put(f"/group-goals/{group_goal.id}/", {"group": group.id, "goal": goal.id, "complete": True}, format="json")
    req.user = admin

    res = view(req, pk=group_goal.id)
    assert res.status_code == 200
    group_goal.refresh_from_db()
    assert group_goal.complete is True

@pytest.mark.django_db
def test_group_goal_destroy_forbidden_for_non_admin(user, group_goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"delete": "destroy"})
    req = factory.delete(f"/group-goals/{group_goal.id}/")
    req.user = user

    res: Response = view(req, pk=group_goal.id)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_group_goal_destroy_admin(admin, group_goal):
    factory = APIRequestFactory()
    view = GroupGoalViewSet.as_view({"delete": "destroy"})
    req = factory.delete(f"/group-goals/{group_goal.id}/")
    req.user = admin

    res = view(req, pk=group_goal.id)
    assert res.status_code == 204
    assert not GroupGoal.objects.filter(id=group_goal.id).exists()

@pytest.mark.django_db
def test_user_group_list_authenticated(user):
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"get": "list"})
    req = factory.get("/user-groups/")
    req.user = user

    res = view(req)
    assert res.status_code == 200
    
@pytest.mark.django_db
def test_user_group_list_unauthenticated():
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"get": "list"})
    req = factory.get("/user-groups/")
    req.user = None

    res: Response = view(req)
    assert res.status_code == 401
    assert res.data["detail"].code == "not_authenticated"

@pytest.mark.django_db
def test_user_group_create_forbidden_for_non_admin(user, group):
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"post": "create"})
    req = factory.post("/user-groups/", {"user": user.id, "group": group.id})
    req.user = user

    res: Response = view(req)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_user_group_create_admin(admin, user, group):
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"post": "create"})
    req = factory.post("/user-groups/", {"user": user.id, "group": group.id}, format="json")
    req.user = admin

    res = view(req)
    assert res.status_code == 201
    assert UserGroup.objects.filter(user=user, group=group).exists()

@pytest.mark.django_db
def test_user_group_update_forbidden_for_non_admin(user, user_group, group):
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"put": "update"})
    req = factory.put(f"/user-groups/{user_group.id}/", {"user": user.id, "group": group.id}, format="json")
    req.user = user

    res = view(req, pk=user_group.id)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_user_group_update_admin(admin, user_group, user, group):
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"put": "update"})
    req = factory.put(f"/user-groups/{user_group.id}/", {"user": user.id, "group": group.id}, format="json")
    req.user = admin

    res = view(req, pk=user_group.id)
    assert res.status_code == 200

@pytest.mark.django_db
def test_user_group_destroy_forbidden_for_non_admin(user, user_group):
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"delete": "destroy"})
    req = factory.delete(f"/user-groups/{user_group.id}/")
    req.user = user

    res: Response = view(req, pk=user_group.id)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_user_group_destroy_admin(admin, user_group):
    factory = APIRequestFactory()
    view = UserGroupViewset.as_view({"delete": "destroy"})
    req = factory.delete(f"/user-groups/{user_group.id}/")
    req.user = admin

    res = view(req, pk=user_group.id)
    assert res.status_code == 204
    assert not UserGroup.objects.filter(id=user_group.id).exists()