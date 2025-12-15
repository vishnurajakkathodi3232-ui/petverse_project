from django.contrib import admin
from .models import Pet, News, Appointment

from .models import OwnedPet
admin.site.register(OwnedPet)

admin.site.register(Pet)
admin.site.register(News)
admin.site.register(Appointment)
