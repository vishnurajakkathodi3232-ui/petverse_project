# core/views.py  — fixed (Option A: keep structure, fix bugs)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone

from .models import Pet, News, Appointment, OwnedPet, AdoptionRequest

User = get_user_model()


def home(request):
    pets = Pet.objects.all()[:6]        # show latest 6 pets
    news = News.objects.all()[:3]       # show latest 3 news items
    return render(request, "core/home.html", {
        "pets": pets,
        "news": news,
    })


def make_appointment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        date = request.POST.get("date")
        service = request.POST.get("service")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        Appointment.objects.create(
            name=name,
            email=email,
            date=date,
            service=service,
            phone=phone,
            message=message
        )

        return redirect("home")

    return redirect("home")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        role = request.POST.get("role")

        # NEW: Pet ownership fields
        owns_pet = request.POST.get("owns_pet")
        pet_name = request.POST.get("pet_name")
        pet_type = request.POST.get("pet_type")
        pet_image = request.FILES.get("pet_image")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        # Save additional user fields
        user.first_name = full_name
        user.phone = phone
        user.address = address
        user.role = role

        # If user owns a pet -> create Pet then OwnedPet (fix: OwnedPet expects a Pet instance)
        if owns_pet == "yes" and pet_name:
            user.has_pet = True
            user.save()

            # Create a Pet instance for owner's pet
            pet = Pet.objects.create(
                name=pet_name,
                category=pet_type or "Unknown",
                description="Owner provided pet",
                image=pet_image,
                is_available=False,
                added_by=user  # treat owner's pet as added by the user
            )

            # Link OwnedPet to that Pet instance
            OwnedPet.objects.create(
                owner=user,
                pet=pet,
                is_listed_for_adoption=False
            )
        else:
            user.has_pet = False
            user.save()

        # Login user
        login(request, user)
        return redirect("home")

    return render(request, "core/signup.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")

        return render(request, "core/login.html", {"error": "Invalid credentials"})

    return render(request, "core/login.html")


def user_logout(request):
    logout(request)
    return redirect("home")


@login_required
def adopter_dashboard(request):
    # Allow only adopters
    if request.user.role != "adopter":
        return redirect("home")

    return render(request, "core/dashboard_adopter.html")


@login_required
def adopter_profile(request):
    # Only adopters can access this page
    if request.user.role != "adopter":
        return redirect("home")

    return render(request, "core/profile_adopter.html")


@login_required
def adopter_adoptions(request):
    # Only adopters can access this
    if request.user.role != "adopter":
        return redirect("home")

    return render(request, "core/adoptions_adopter.html")


@login_required
def adopter_favorites(request):
    if request.user.role != "adopter":
        return redirect("home")

    return render(request, "core/favorites_adopter.html")


@login_required
def adopter_appointments(request):
    if request.user.role != "adopter":
        return redirect("home")

    return render(request, "core/appointments_adopter.html")


@login_required
def owner_dashboard(request):
    # Only users who actually have a pet can access owner services
    if not getattr(request.user, "has_pet", False):
        return redirect("home")

    return render(request, "core/dashboard_owner.html")


@login_required
def owner_add_pet(request):
    # Owner must have owner role/flag
    if not getattr(request.user, "has_pet", False):
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        pet_type = request.POST.get("pet_type") or request.POST.get("category")  # handle possible name mismatch
        image = request.FILES.get("image")
        description = request.POST.get("description", "Owner added pet")

        # 1) Create Pet record (owners' pets are Pet instances too)
        pet = Pet.objects.create(
            name=name,
            category=pet_type or "Unknown",
            description=description,
            image=image,
            is_available=False,     # owner pets are NOT public by default
            added_by=request.user
        )

        # 2) Create OwnedPet linking the pet to the owner
        OwnedPet.objects.create(
            owner=request.user,
            pet=pet,
            is_listed_for_adoption=False
        )

        return redirect("owner_pets")

    return render(request, "core/owner_add_pet.html")


@login_required
def owner_adoptions(request):
    if not getattr(request.user, "has_pet", False):
        return redirect("home")

    # Placeholder for now — will show real requests later
    return render(request, "core/owner_adoptions.html")


@login_required
def owner_appointments(request):
    if not getattr(request.user, "has_pet", False):
        return redirect("home")

    return render(request, "core/owner_appointments.html")


@login_required
def owner_profile(request):
    # Only users with pets can access owner role pages
    if not getattr(request.user, "has_pet", False):
        return redirect("home")

    return render(request, "core/owner_profile.html")


@login_required
def owner_approve_request(request, req_id):
    """
    Approve an adoption request that targets a pet owned by the logged-in owner.
    We try to find the OwnedPet record for this owner and the requested pet,
    transfer ownership to the adopter and delete the original OwnedPet.
    """
    req = get_object_or_404(AdoptionRequest, id=req_id)

    # Find the OwnedPet record for this pet and owner
    owned = OwnedPet.objects.filter(pet=req.pet, owner=request.user).first()
    if not owned:
        # Owner is not the owner of this pet -> deny
        return redirect("home")

    # Ensure the owner in DB matches the logged in owner (sanity)
    if owned.owner != request.user:
        return redirect("home")

    # Update request status
    req.status = "approved"
    req.save()

    # Transfer ownership: create OwnedPet for adopter (attach same Pet instance)
    OwnedPet.objects.create(
        owner=req.adopter,
        pet=req.pet,
        is_listed_for_adoption=False
    )

    # Remove original owner's OwnedPet record
    owned.delete()

    # Mark the Pet as unavailable to prevent further adoption attempts
    req.pet.is_available = False
    req.pet.save()

    return redirect("owner_adoptions")


@login_required
def owner_reject_request(request, req_id):
    req = get_object_or_404(AdoptionRequest, id=req_id)

    owned = OwnedPet.objects.filter(pet=req.pet, owner=request.user).first()
    if not owned:
        return redirect("home")

    # Only the owner of that pet can reject
    if owned.owner != request.user:
        return redirect("home")

    req.status = "declined"
    req.save()

    return redirect("owner_adoptions")
@login_required
def send_adoption_request(request, pet_id):
    # Only adopters can send requests
    if request.user.role != "adopter":
        return redirect("home")

    pet = get_object_or_404(Pet, id=pet_id)

    # Prevent duplicate requests
    existing = AdoptionRequest.objects.filter(adopter=request.user, pet=pet).first()
    if existing:
        return render(request, "core/request_status.html", {
            "message": "You have already sent a request for this pet!"
        })

    if request.method == "POST":
        message = request.POST.get("message")
        AdoptionRequest.objects.create(
            adopter=request.user,
            pet=pet,
            message=message,
        )
        return render(request, "core/request_status.html", {
            "message": "Your adoption request has been sent!"
        })

    return render(request, "core/send_adoption_request.html", {"pet": pet})


def shelter_signup(request):
    if request.method == "POST":
        shelter_name = request.POST.get("shelter_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        description = request.POST.get("description")
        logo = request.FILES.get("logo")

        # Create shelter user
        user = User.objects.create_user(
            username=shelter_name.replace(" ", "").lower(),
            email=email,
            password=password,
        )

        # Assign role
        user.role = "shelter"
        user.first_name = shelter_name
        user.phone = phone
        user.address = address
        user.save()

        # Save logo (as profile image for now)
        if logo:
            user.profile_image = logo
            user.save()

        # Login immediately (for now)
        login(request, user)
        return redirect("shelter_dashboard")

    return render(request, "core/shelter_signup.html")


@login_required
def shelter_dashboard(request):
    if request.user.role != "shelter":
        return redirect("home")

    return render(request, "core/dashboard_shelter.html")


@login_required
def shelter_pets(request):
    if request.user.role != "shelter":
        return redirect("home")

    pets = Pet.objects.filter(added_by=request.user)
    return render(request, "core/shelter_pets.html", {"pets": pets})


@login_required
def owner_pets(request):
    # Allow access if user is owner OR user has at least 1 pet
    has_pets = OwnedPet.objects.filter(owner=request.user).exists()

    if request.user.role not in ["owner"] and not has_pets:
        return redirect("home")

    pets = OwnedPet.objects.filter(owner=request.user)
    return render(request, "core/owner_pets.html", {"pets": pets})


@login_required
def shelter_add_pet(request):
    if request.user.role != "shelter":
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        category = request.POST.get("category")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        Pet.objects.create(
            name=name,
            category=category,
            description=description,
            image=image,
            added_by=request.user,  # IMPORTANT
        )

        return redirect("shelter_pets")

    return render(request, "core/shelter_add_pet.html")


@login_required
def shelter_edit_pet(request, pet_id):
    if request.user.role != "shelter":
        return redirect("home")

    pet = get_object_or_404(Pet, id=pet_id, added_by=request.user)

    if request.method == "POST":
        pet.name = request.POST.get("name")
        pet.category = request.POST.get("category")
        pet.description = request.POST.get("description")

        image = request.FILES.get("image")
        if image:
            pet.image = image

        pet.save()
        return redirect("shelter_pets")

    return render(request, "core/shelter_edit_pet.html", {"pet": pet})


@login_required
def shelter_adoptions(request):
    if request.user.role != "shelter":
        return redirect("home")

    # All requests for pets added by this shelter
    requests = AdoptionRequest.objects.filter(pet__added_by=request.user)

    return render(request, "core/shelter_adoptions.html", {"requests": requests})
@login_required
def shelter_profile(request):
    if request.user.role != "shelter":
        return redirect("home")

    return render(request, "core/shelter_profile.html")


@login_required
def approve_request(request, req_id):
    """
    Approve a shelter adoption request (shelter -> adopter).
    This assumes the AdoptionRequest.pet is a Pet instance added by shelter.
    """
    req = get_object_or_404(AdoptionRequest, id=req_id)

    # Ensure only the shelter who added the pet can approve this request
    if req.pet.added_by != request.user:
        return redirect("home")

    # Update request status
    req.status = "approved"
    req.save()

    # Convert adopted pet into OwnedPet for the adopter (attach same Pet instance)
    OwnedPet.objects.create(
        owner=req.adopter,
        pet=req.pet,
        is_listed_for_adoption=False
    )

    # Mark shelter pet as unavailable
    req.pet.is_available = False
    req.pet.save()

    return redirect("shelter_adoptions")


@login_required
def decline_request(request, req_id):
    req = get_object_or_404(AdoptionRequest, id=req_id)

    if req.pet.added_by != request.user:
        return redirect("home")

    req.status = "declined"
    req.save()
    return redirect("shelter_adoptions")


@login_required
def adopter_favorites(request):
    if request.user.role != "adopter":
        return redirect("home")

    return render(request, "core/favorites_adopter.html")


def pets_list(request):
    pets = Pet.objects.filter(is_available=True)
    return render(request, "core/pets_list.html", {"pets": pets})


def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, "core/pet_detail.html", {"pet": pet})


@login_required
def shelter_delete_pet(request, pet_id):
    if request.user.role != "shelter":
        return redirect("home")

    pet = get_object_or_404(Pet, id=pet_id, added_by=request.user)
    pet.delete()
    return redirect("shelter_pets")


def owned_pet_detail(request, pet_id):
    pet = get_object_or_404(OwnedPet, id=pet_id)
    return render(request, "core/owned_pet_detail.html", {"pet": pet})
