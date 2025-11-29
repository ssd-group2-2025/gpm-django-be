from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_https_hostname
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class User(AbstractUser):
    matricola = models.CharField(
        verbose_name='Matricola',
        unique=True,
        null=False,
        validators=[RegexValidator(r'^\d{6}$', "La matricola deve avere 6 cifre numeriche")]
    )

    group = models.ForeignKey(
        "Group",
        on_delete=models.PROTECT,
        related_name="members",
        null=True,
        blank=True
    )

class Topic(models.Model):
    title = models.CharField(max_length=100)

class Group(models.Model):
    name = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name='groups')
    link_django = models.URLField(validators=[validate_https_hostname])
    link_tui = models.URLField(validators=[validate_https_hostname])
    link_gui = models.URLField(validators=[validate_https_hostname])

class Goal(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    points = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

class GroupGoals(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='goals')
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name='groups')
    complete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Group Goal"
        verbose_name_plural = "Group Goals"