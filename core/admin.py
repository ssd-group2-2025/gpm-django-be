from django.contrib import admin
from .models import User, Topic, Group, Goal, GroupGoals


class GroupGoalsInline(admin.TabularInline):
    model = GroupGoals
    extra = 0


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "link_django", "link_tui", "link_gui")
    list_filter = ("topic",)
    search_fields = ("name",)
    inlines = [GroupGoalsInline]


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "points")
    search_fields = ("title",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)


@admin.register(GroupGoals)
class GroupGoalsAdmin(admin.ModelAdmin):
    list_display = ("group", "goal", "complete")
    list_filter = ("complete", "group", "goal")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "group", "is_staff")
    list_filter = ("group", "is_staff")
    search_fields = ("username", "email")
