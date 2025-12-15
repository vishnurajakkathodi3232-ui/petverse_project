from django.db import models
from django.conf import settings
from django.contrib.auth.models import User   # used for OwnedPet.owner


class Pet(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)   # Dog, Cat, etc.
    description = models.TextField()
    image = models.ImageField(upload_to='pets/')
    is_available = models.BooleanField(default=True)

    # NEW FIELD → identifies which shelter added the pet
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shelter_pets"
    )

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return self.title


class Appointment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    service = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.date}"


class OwnedPet(models.Model):
   
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    acquired_at = models.DateTimeField(auto_now_add=True)

    # NEW FIELD
    is_listed_for_adoption = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pet.name} owned by {self.owner.username}"


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    adopter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.adopter.username} → {self.pet.name} ({self.status})"
