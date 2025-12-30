from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ServiceAppointment
from pets.models import OwnedPet


@login_required
def owner_service_appointments(request):
    """
    Shows service appointments booked for pets owned by the logged-in owner.
    """

    # Get pets owned by this user
    owned_pets = OwnedPet.objects.filter(owner=request.user)

    # Fetch service appointments for those pets
    appointments = ServiceAppointment.objects.filter(
        pet__in=owned_pets
    ).select_related('service', 'pet').order_by('-date', '-time')

    context = {
        'appointments': appointments,
    }

    return render(
        request,
        'services/owner_service_appointments.html',
        context
    )
