from django.urls import path
from . import views

app_name = 'adoptions'

urlpatterns = [
    path('', views.temp_adoptions_home, name='adoptions_home'),
]
