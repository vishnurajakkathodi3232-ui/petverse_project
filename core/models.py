from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


# =========================
# PET (Shelter Pet)
# =========================
class Pet(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='pets/')
    is_available = models.BooleanField(default=False)

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
# APPOINTMENT (Public)
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
# OWNED PET (Owner Pet)
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

    is_listed_for_adoption = models.BooleanField(default=False)

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

    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shelter_adoption_requests"
    )

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
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.pet and not self.owned_pet:
            raise ValidationError("Either pet or owned_pet must be selected.")
        if self.pet and self.owned_pet:
            raise ValidationError("Only one of pet or owned_pet can be selected.")

    @property
    def target_pet_name(self):
        return self.pet.name if self.pet else self.owned_pet.pet.name

    @property
    def adoption_type(self):
        return "Shelter" if self.pet else "Owner"

    def __str__(self):
        return f"{self.adopter.username} → {self.target_pet_name}"


# =========================
# SERVICE CATEGORY
# =========================
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================
# SERVICE (Grooming / Vet)
# =========================
class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name="services"
    )

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# =========================
# SERVICE APPOINTMENT
# =========================
class ServiceAppointment(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_appointments"
    )

    owned_pet = models.ForeignKey(
        OwnedPet,
        on_delete=models.CASCADE,
        related_name="service_appointments"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} | {self.owned_pet.pet.name} | {self.appointment_date}"

User = settings.AUTH_USER_MODEL


class ChatRoom(models.Model):
    adoption_request = models.OneToOneField(
        AdoptionRequest,
        on_delete=models.CASCADE,
        related_name="chat_room"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for Request #{self.adoption_request.id}"


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"


class Payment(models.Model):
    PAYMENT_FOR_CHOICES = (
        ("appointment", "Appointment"),
        ("adoption", "Adoption"),
        ("shop", "Shop"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    # Who paid
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments_made"
    )

    # Who receives money (for adoption only)
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_received"
    )

    payment_for = models.CharField(
        max_length=20,
        choices=PAYMENT_FOR_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # Generic references (ONLY ONE will be filled)
    appointment = models.ForeignKey(
        "ServiceAppointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    adoption_request = models.ForeignKey(
        "AdoptionRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    order = models.ForeignKey(
    "shop.Order",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="core_payments"
)

    

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_for} | ₹{self.amount} | {self.status}"
