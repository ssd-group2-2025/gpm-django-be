from rest_framework.routers import SimpleRouter
from .views import GroupViewSet

router = SimpleRouter()

router.register('group', GroupViewSet, basename='group')

urlpatterns = router.urls