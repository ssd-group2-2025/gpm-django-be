from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator

class User(AbstractUser):
    matricola = models.CharField(
        verbose_name='Matricola',
        unique=True,
        null=False,
        blank=False,
        validators=[RegexValidator(r'^\d{6}$', "The matricola must contain exactly 6 digits")]
    )

    email = models.CharField(
        unique=True,
        null=False,
        blank=False,
        validators=[EmailValidator()]
    )