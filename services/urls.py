from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.temp_services_home, name='services_home'),
]
