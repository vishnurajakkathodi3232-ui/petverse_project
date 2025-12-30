from django.contrib import admin
from .models import (
    Pet,
    OwnedPet,
    Appointment,
    News,
    AdoptionRequest,
    ServiceCategory,
    Service,
    ServiceAppointment,
)

admin.site.register(Pet)
admin.site.register(OwnedPet)
admin.site.register(Appointment)
admin.site.register(News)
admin.site.register(AdoptionRequest)

# ✅ SERVICE SYSTEM
admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(ServiceAppointment)

from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("user__username",)
    ordering = ("-created_at",)
