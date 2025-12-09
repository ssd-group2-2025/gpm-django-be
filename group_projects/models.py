from django.db import models
from .validators import validate_https_hostname
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from users.models import User

class Topic(models.Model):
    title = models.CharField(max_length=100)

class GroupProject(models.Model):
    name = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name='group_projects')
    link_django = models.URLField(validators=[validate_https_hostname], default='https://example.com', blank=True)
    link_tui = models.URLField(validators=[validate_https_hostname], default='https://example.com', blank=True)
    link_gui = models.URLField(validators=[validate_https_hostname], default='https://example.com', blank=True)

class Goal(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    points = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

class GroupGoal(models.Model):
    group = models.ForeignKey(GroupProject, on_delete=models.PROTECT, related_name='goals')
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name='group_projects')
    complete = models.BooleanField(default=False)

class UserGroup(models.Model):
    group = models.ForeignKey(GroupProject, on_delete=models.PROTECT, related_name='users')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='group_projects')