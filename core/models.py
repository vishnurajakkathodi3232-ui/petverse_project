from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


# =========================
# PET (Shelter Pet)
# =========================
class Pet(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)   # Dog, Cat, etc.
    description = models.TextField()
    image = models.ImageField(upload_to='pets/')
    is_available = models.BooleanField(default=False)

    # Shelter user who added the pet
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shelter_pets"
    )

    def __str__(self):
        return self.name


# =========================
# NEWS
# =========================
class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return self.title


# =========================
# APPOINTMENT
# =========================
class Appointment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    service = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.date}"


# =========================
# OWNED PET (Owner-listed Pet)
# =========================
class OwnedPet(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_pets"
    )

    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name="ownerships"
    )

    acquired_at = models.DateTimeField(auto_now_add=True)

    # NORMALIZED FIELD
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pet.name} owned by {self.owner.username}"


# =========================
# ADOPTION REQUEST
# =========================
class AdoptionRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    adopter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="adoption_requests"
    )

    # Shelter pet adoption
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shelter_adoption_requests"
    )

    # Owner pet adoption
    owned_pet = models.ForeignKey(
        OwnedPet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owner_adoption_requests"
    )

    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ---------- VALIDATION ----------
    def clean(self):
        """
        Exactly ONE of (pet, owned_pet) must be set.
        """
        if not self.pet and not self.owned_pet:
            raise ValidationError(
                "Either pet or owned_pet must be selected."
            )

        if self.pet and self.owned_pet:
            raise ValidationError(
                "Only one of pet or owned_pet can be selected."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ---------- HELPERS ----------
    @property
    def target_pet_name(self):
        if self.pet:
            return self.pet.name
        if self.owned_pet:
            return self.owned_pet.pet.name
        return "N/A"

    @property
    def adoption_type(self):
        return "Shelter" if self.pet else "Owner"

    def __str__(self):
        return f"{self.adopter.username} → {self.target_pet_name}"
