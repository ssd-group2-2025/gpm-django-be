from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from users.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


def logout_view(request):
    logout(request)
    next_url = request.GET.get('next', '/api/docs/')
    return redirect(next_url)


schema_view = get_schema_view(
   openapi.Info(
      title="GPM API",
      default_version='v1',
      description="Group Project Manager",
      terms_of_service="",
      contact=openapi.Contact(email="vincenzorizzomy@gmail.com"),
      license=openapi.License(name="MIT"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='rest_framework/login.html'), name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('api/v1/auth/logout/', include('dj_rest_auth.urls')),  # solo per logout
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/v1/auth/login/', CustomTokenObtainPairView.as_view(), name='custom_login'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include("group_projects.urls")),
    path('api/v1/', include("users.urls"))
]
