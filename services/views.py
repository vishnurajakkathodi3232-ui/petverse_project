from django.http import HttpResponse

def temp_services_home(request):
    return HttpResponse("Services app working!")
