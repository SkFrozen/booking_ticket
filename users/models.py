from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(blank=True)
    notifications = models.BooleanField(default=False)

    class Meta:
        db_table = "users"
