from rest_framework.routers import SimpleRouter
from .views import GroupViewSet, UserViewSet, TopicViewSet, GoalViewSet, GroupGoalsViewSet

router = SimpleRouter()

router.register('groups', GroupViewSet, basename='group')
router.register('users', UserViewSet, basename='user')
router.register('topics', TopicViewSet, basename='topic')
router.register('goals', GoalViewSet, basename='goal')
router.register('group-goals', GroupGoalsViewSet, basename='group-goal')

urlpatterns = router.urls