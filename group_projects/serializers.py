from rest_framework.serializers import ModelSerializer
from .models import GroupProject, Topic, Goal, GroupGoal, UserGroup

class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
        read_only_fields = ['id']

class GoalSerializer(ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['id']

class GroupGoalsSerializer(ModelSerializer):
    class Meta:
        model = GroupGoal
        fields = '__all__'
        read_only_fields = ['id']

class GroupProjectSerializer(ModelSerializer):
    class Meta:
        model = GroupProject
        fields = ['id', 'name', 'link_django', 'link_tui', 'link_gui', 'topic']
        read_only_fields = ['id']

class UserGroupSerializer(ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'
        read_only_fields = ['id']

