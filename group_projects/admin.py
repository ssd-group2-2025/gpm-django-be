from django.contrib import admin
from .models import Topic, GroupProject, Goal, GroupGoal


class GroupGoalsInline(admin.TabularInline):
    model = GroupGoal
    extra = 0


@admin.register(GroupProject)
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


@admin.register(GroupGoal)
class GroupGoalsAdmin(admin.ModelAdmin):
    list_display = ("group", "goal", "complete")
    list_filter = ("complete", "group", "goal")

