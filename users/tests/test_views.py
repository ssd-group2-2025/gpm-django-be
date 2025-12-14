import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from users.views import CustomLogoutView, CustomTokenObtainPairView, UserViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

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

@pytest.mark.django_db
def test_token_obtain_success_sets_refresh_cookie():
    factory = APIRequestFactory()
    view = CustomTokenObtainPairView.as_view()

    password = "strong-password"
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password=password,
        is_active=True,
    )

    credentials = {
        "username": user.username,
        "password": password,
    }

    req = factory.post("/auth/login/", credentials, format="json")

    res: Response = view(req)

    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data

    cookie_name = settings.REST_AUTH.get(
        "JWT_AUTH_REFRESH_COOKIE", "jwt-refresh"
    )

    assert cookie_name in res.cookies
    assert res.cookies[cookie_name]["httponly"] is True

@pytest.mark.django_db
def test_token_obtain_invalid_credentials():
    factory = APIRequestFactory()
    view = CustomTokenObtainPairView.as_view()

    User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="correct-password",
    )

    req = factory.post(
        "/auth/login/",
        {
            "username": "testuser",
            "password": "wrong-password",
        },
        format="json",
    )

    res: Response = view(req)

    assert res.status_code == 401
    assert "access" not in res.data
    assert "refresh" not in res.data
    assert len(res.cookies) == 0

@pytest.mark.django_db
def test_token_obtain_missing_fields():
    factory = APIRequestFactory()
    view = CustomTokenObtainPairView.as_view()

    req = factory.post(
        "/auth/login/",
        {},
        format="json",
    )

    res: Response = view(req)

    assert res.status_code == 400
    assert "username" in res.data or "password" in res.data
    assert len(res.cookies) == 0

@pytest.mark.django_db
def test_logout_with_refresh_cookie():
    factory = APIRequestFactory()
    view = CustomLogoutView.as_view()

    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="test-password",
    )

    refresh = RefreshToken.for_user(user)

    cookie_name = settings.REST_AUTH.get(
        "JWT_AUTH_REFRESH_COOKIE", "jwt-refresh"
    )

    req = factory.post("/auth/logout/")
    req.COOKIES[cookie_name] = str(refresh)

    res: Response = view(req)

    assert res.status_code == status.HTTP_200_OK
    assert res.data["detail"] == "Successfully logged out."
    assert cookie_name in res.cookies
    assert res.cookies[cookie_name]["max-age"] == 0

@pytest.mark.django_db
def test_logout_with_refresh_in_body():
    factory = APIRequestFactory()
    view = CustomLogoutView.as_view()

    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="test-password",
    )

    refresh = RefreshToken.for_user(user)

    req = factory.post(
        "/auth/logout/",
        {"refresh": str(refresh)},
        format="json",
    )

    res: Response = view(req)

    assert res.status_code == status.HTTP_200_OK
    assert res.data["detail"] == "Successfully logged out."

@pytest.mark.django_db
def test_logout_without_refresh_token():
    factory = APIRequestFactory()
    view = CustomLogoutView.as_view()

    req = factory.post("/auth/logout/")

    res: Response = view(req)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.data["detail"] == "Refresh token was not included in cookie data."

@pytest.mark.django_db
def test_logout_with_invalid_refresh_token():
    factory = APIRequestFactory()
    view = CustomLogoutView.as_view()

    req = factory.post(
        "/auth/logout/",
        {"refresh": "invalid.token.value"},
        format="json",
    )

    res: Response = view(req)

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data["detail"] == "Token is invalid or expired."

@pytest.mark.django_db
def test_logout_blacklists_refresh_token():
    factory = APIRequestFactory()
    view = CustomLogoutView.as_view()

    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="test-password",
    )

    refresh = RefreshToken.for_user(user)
    token_str = str(refresh)

    req = factory.post(
        "/auth/logout/",
        {"refresh": token_str},
        format="json",
    )

    res = view(req)
    assert res.status_code == 200

    req2 = factory.post(
        "/auth/logout/",
        {"refresh": token_str},
        format="json",
    )

    res2 = view(req2)
    assert res2.status_code == 400