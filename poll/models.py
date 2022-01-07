from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


class Candidate(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    fraction = models.CharField(max_length=20)
    biography = models.TextField()
    targets = models.CharField(max_length=1000)
    telephone = models.CharField(max_length=20)
    votes = models.IntegerField(default=0)
    refusal_reason = models.TextField(default='')
    moderated = models.BooleanField(default=False)
    avatar = models.ImageField(default='default-avatar.jpeg', null=True, blank=True)


class AdminData(models.Model):
    instruction = models.TextField(default='There is no instruction')

    # This function lets saving only one object of the class
    def save(self, *args, **kwargs):
        if not self.pk and AdminData.objects.exists():
            raise ValidationError('Can be only one AdminData instance')
        return super().save(*args, **kwargs)


class User(AbstractUser):
    checked_by_moderator = models.BooleanField(default=False)

    ELECTOR = 1
    CANDIDATE = 2
    MODERATOR = 3

    ROLE_CHOICES = (
        (ELECTOR, 'Elector'),
        (CANDIDATE, 'Candidate'),
        (MODERATOR, 'Moderator'),
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)