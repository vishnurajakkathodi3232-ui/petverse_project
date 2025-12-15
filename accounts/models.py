from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('adopter', 'Adopter'),
        ('owner', 'Owner'),
        ('shelter', 'Shelter'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='adopter')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # NEW FIELD ↓↓↓
    has_pet = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
