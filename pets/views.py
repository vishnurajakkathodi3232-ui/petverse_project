from django.http import HttpResponse

def temp_pets_home(request):
    return HttpResponse("Pets app working!")
