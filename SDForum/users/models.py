from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    ROLE_CHOICES = [
        ("STUDENT","student"),
        ("MODERATOR", "moderator"),
    ]

    user = models.OneToOneField(User, on_delete = models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='STUDENT'
    )
    avatar = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    @property
    def is_moderator(self):
        return self.role=="MODERATOR"