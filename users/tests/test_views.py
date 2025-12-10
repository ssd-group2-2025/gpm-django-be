import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
from users.models import User
from users.views import UserViewSet

@pytest.fixture
def user():
    return User.objects.create_user(
        username="user",
        email="user@example.com",
        password="pass123",
        matricola="123456"
    )

@pytest.fixture
def admin():
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="pass123",
        matricola="654321"
    )

@pytest.mark.django_db
def test_user_list_authenticated(user, admin):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"get": "list"})
    req = factory.get("/users/")
    req.user = user

    res = view(req)
    assert res.status_code == 200
    usernames = [u["username"] for u in res.data]
    # admin is superuser, should be excluded from list
    assert "admin" not in usernames
    assert "user" in usernames

@pytest.mark.django_db
def test_user_list_unauthenticated(user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"get": "list"})
    req = factory.get("/users/")
    req.user = None

    res: Response = view(req)
    assert res.status_code == 401
    assert res.data["detail"].code == "not_authenticated"

@pytest.mark.django_db
def test_user_retrieve_authenticated(user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"get": "retrieve"})
    req = factory.get(f"/users/{user.id}/")
    req.user = user

    res = view(req, pk=user.id)
    assert res.status_code == 200
    assert res.data["id"] == user.id

@pytest.mark.django_db
def test_user_create_forbidden_for_non_admin(user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"post": "create"})
    req = factory.post(
        "/users/",
        {"username": "newuser", "email": "newuser@example.com", "password": "pass123", "matricola": "222222"}
    )
    req.user = user

    res: Response = view(req)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_user_create_admin(admin):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"post": "create"})
    req = factory.post(
        "/users/",
        {"username": "newuser", "email": "newuser@example.com", "password": "pass123", "matricola": "222222"},
        format="json"
    )
    req.user = admin

    res = view(req)
    assert res.status_code == 201
    assert User.objects.filter(username="newuser").exists()

@pytest.mark.django_db
def test_user_update_forbidden_for_non_admin(user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"put": "update"})
    req = factory.put(
        f"/users/{user.id}/",
        {"username": "updated", "email": user.email, "matricola": user.matricola},
        format="json"
    )
    req.user = user

    res: Response = view(req, pk=user.id)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_user_update_admin(admin, user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"put": "update"})
    req = factory.put(
        f"/users/{user.id}/",
        {"username": "updated", "email": user.email, "matricola": user.matricola},
        format="json"
    )
    req.user = admin

    res = view(req, pk=user.id)
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.username == "updated"

@pytest.mark.django_db
def test_user_destroy_forbidden_for_non_admin(user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"delete": "destroy"})
    req = factory.delete(f"/users/{user.id}/")
    req.user = user

    res: Response = view(req, pk=user.id)
    assert res.status_code == 403
    assert res.data["detail"].code == "permission_denied"

@pytest.mark.django_db
def test_user_destroy_admin(admin, user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"delete": "destroy"})
    req = factory.delete(f"/users/{user.id}/")
    req.user = admin

    res = view(req, pk=user.id)
    assert res.status_code == 204
    assert not User.objects.filter(id=user.id).exists()

@pytest.mark.django_db
def test_user_me_authenticated(user):
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"get": "me"})
    req = factory.get("/users/me/")
    req.user = user

    res = view(req)
    assert res.status_code == 200
    assert res.data["id"] == user.id

@pytest.mark.django_db
def test_user_me_unauthenticated():
    factory = APIRequestFactory()
    view = UserViewSet.as_view({"get": "me"})
    req = factory.get("/users/me/")
    req.user = None

    res: Response = view(req)
    assert res.status_code == 401
    assert res.data["detail"].code == "not_authenticated"