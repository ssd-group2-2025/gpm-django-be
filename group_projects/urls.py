from rest_framework.routers import SimpleRouter
from .views import GroupProjectViewSet, TopicViewSet, GoalViewSet, GroupGoalViewSet, UserGroupViewset

router = SimpleRouter()

router.register('groups', GroupProjectViewSet, basename='group')
router.register('topics', TopicViewSet, basename='topic')
router.register('goals', GoalViewSet, basename='goal')
router.register('group-goals', GroupGoalViewSet, basename='group-goal')
router.register('group-users', UserGroupViewset, basename='group-user')

urlpatterns = router.urls