from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    matricola = models.CharField(
        verbose_name='Matricola',
        unique=True,
        null=False,
        blank=False,
        validators=[RegexValidator(r'^\d{6}$', "La matricola deve avere 6 cifre numeriche")]
    )