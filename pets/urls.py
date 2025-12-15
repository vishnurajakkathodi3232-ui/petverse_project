from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    # temporary placeholder view until we build real pages
    path('', views.temp_pets_home, name='pets_home'),
]
