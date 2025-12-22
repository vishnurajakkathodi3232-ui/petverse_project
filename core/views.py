# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model

from .models import (
    Pet,
    News,
    Appointment,
    OwnedPet,
    AdoptionRequest,
)

User = get_user_model()

# ======================================================
# PUBLIC PAGES
# ======================================================
from itertools import chain
from .models import Pet, OwnedPet, News


def home(request):
    # Shelter pets that are available
    shelter_pets = Pet.objects.filter(is_available=True)

    # Owner pets that are available (use the related Pet object)
    owner_pets = OwnedPet.objects.filter(
        is_available=True
    ).select_related("pet")

    # Normalize owner pets to look like Pet objects
    owner_pet_list = [op.pet for op in owner_pets]

    # Combine both sources
    combined_pets = list(chain(shelter_pets, owner_pet_list))[:6]

    news = News.objects.all()[:3]

    return render(
        request,
        "core/home.html",
        {
            "pets": combined_pets,
            "news": news,
        }
    )

def make_appointment(request):
    if request.method == "POST":
        Appointment.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            date=request.POST.get("date"),
            service=request.POST.get("service"),
            phone=request.POST.get("phone"),
            message=request.POST.get("message"),
        )
    return redirect("home")


# ======================================================
# AUTH
# ======================================================

def signup(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST.get("username"),
            email=request.POST.get("email"),
            password=request.POST.get("password"),
        )

        user.first_name = request.POST.get("full_name", "")
        user.phone = request.POST.get("phone")
        user.address = request.POST.get("address")
        user.role = request.POST.get("role")
        user.has_pet = False
        user.save()

        login(request, user)
        return redirect("home")

    return render(request, "core/signup.html")


def user_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("home")

        return render(request, "core/login.html", {"error": "Invalid credentials"})

    return render(request, "core/login.html")


def user_logout(request):
    logout(request)
    return redirect("home")


# ======================================================
# ADOPTER
# ======================================================

@login_required
def adopter_dashboard(request):
    if request.user.role != "adopter":
        return redirect("home")
    return render(request, "core/dashboard_adopter.html")


@login_required
def pets_list(request):
    if request.user.role != "adopter":
        return redirect("home")

    shelter_pets = Pet.objects.filter(is_available=True)
    owner_pets = OwnedPet.objects.filter(is_available=True)

    pets = []

    for pet in shelter_pets:
        pets.append({
            "id": pet.id,
            "name": pet.name,
            "category": pet.category,
            "image": pet.image,
            "source": "shelter",
        })

    for owned in owner_pets:
        pets.append({
            "id": owned.id,
            "name": owned.pet.name,
            "category": owned.pet.category,
            "image": owned.pet.image,
            "source": "owner",
        })

    return render(request, "core/pets_list.html", {"pets": pets})


@login_required
def send_adoption_request(request, pet_id=None, owned_pet_id=None):
    if request.user.role != "adopter":
        return redirect("home")

    if pet_id:
        pet = get_object_or_404(Pet, id=pet_id, is_available=True)
        AdoptionRequest.objects.get_or_create(
            adopter=request.user,
            pet=pet,
        )

    if owned_pet_id:
        owned_pet = get_object_or_404(
            OwnedPet,
            id=owned_pet_id,
            is_available=True
        )
        AdoptionRequest.objects.get_or_create(
            adopter=request.user,
            owned_pet=owned_pet,
        )

    return redirect("pets_list")


# ======================================================
# OWNER
# ======================================================

@login_required
def owner_dashboard(request):
    if not OwnedPet.objects.filter(owner=request.user).exists():
        return redirect("home")
    return render(request, "core/dashboard_owner.html")


@login_required
def owner_pets(request):
    pets = OwnedPet.objects.filter(owner=request.user)
    return render(request, "core/owner_pets.html", {"pets": pets})


@login_required
def owner_list_pet(request, pet_id):
    owned_pet = get_object_or_404(
        OwnedPet,
        id=pet_id,
        owner=request.user
    )
    owned_pet.is_available = True
    owned_pet.save()
    return redirect("owner_pets")


@login_required
def owner_unlist_pet(request, pet_id):
    owned_pet = get_object_or_404(
        OwnedPet,
        id=pet_id,
        owner=request.user
    )
    owned_pet.is_available = False
    owned_pet.save()
    return redirect("owner_pets")


# ======================================================
# SHELTER
# ======================================================

@login_required
def shelter_dashboard(request):
    if request.user.role != "shelter":
        return redirect("home")
    return render(request, "core/dashboard_shelter.html")


@login_required
def shelter_pets(request):
    pets = Pet.objects.filter(added_by=request.user)
    return render(request, "core/shelter_pets.html", {"pets": pets})


@login_required
def shelter_add_pet(request):
    if request.method == "POST":
        Pet.objects.create(
            name=request.POST.get("name"),
            category=request.POST.get("category"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
            added_by=request.user,
            is_available=False,
        )
        return redirect("shelter_pets")

    return render(request, "core/shelter_add_pet.html")


# ======================================================
# ADMIN (SUPER ADMIN)
# ======================================================

@login_required
def superadmin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("home")

    return render(request, "core/admin/dashboard.html", {
        "total_users": User.objects.count(),
        "total_pets": Pet.objects.count(),
        "total_requests": AdoptionRequest.objects.count(),
    })


@login_required
def superadmin_users(request):
    if not request.user.is_superuser:
        return redirect("home")

    users = User.objects.all().order_by("-date_joined")
    return render(request, "core/admin/users.html", {"users": users})


@login_required
def superadmin_pets(request):
    if not request.user.is_superuser:
        return redirect("home")

    pets = Pet.objects.all().order_by("-id")
    return render(request, "core/admin/pets.html", {"pets": pets})


@login_required
def superadmin_adoptions(request):
    if not request.user.is_superuser:
        return redirect("home")

    adoptions = AdoptionRequest.objects.select_related(
        "pet", "owned_pet", "adopter"
    ).order_by("-created_at")

    return render(
        request,
        "core/admin/adoptions.html",
        {"adoptions": adoptions}
    )


@login_required
def admin_approve_adoption(request, pk):
    if not request.user.is_superuser:
        return redirect("home")

    adoption = get_object_or_404(AdoptionRequest, pk=pk)
    adoption.status = "approved"
    adoption.save()

    if adoption.pet:
        adoption.pet.is_available = False
        adoption.pet.save()

    if adoption.owned_pet:
        adoption.owned_pet.is_available = False
        adoption.owned_pet.save()

    return redirect("admin_adoptions")


@login_required
def admin_reject_adoption(request, pk):
    if not request.user.is_superuser:
        return redirect("home")

    adoption = get_object_or_404(AdoptionRequest, pk=pk)
    adoption.status = "declined"
    adoption.save()

    return redirect("admin_adoptions")

# ======================================================
# PATCHED STUB VIEWS (URL COMPATIBILITY)
# ======================================================

# ---------- PUBLIC ----------
def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, "core/pet_detail.html", {"pet": pet})


# ---------- ADOPTER ----------
@login_required
def adopter_profile(request):
    if request.user.role != "adopter":
        return redirect("home")
    return render(request, "core/profile_adopter.html")

@login_required
def adopter_adoptions(request):
    if request.user.role != "adopter":
        return redirect("home")

    requests = AdoptionRequest.objects.filter(
        adopter=request.user
    ).select_related(
        "pet",
        "owned_pet",
        "owned_pet__pet"
    ).order_by("-created_at")

    return render(
        request,
        "core/adoptions_adopter.html",
        {"requests": requests}
    )


@login_required
def adopter_appointments(request):
    if request.user.role != "adopter":
        return redirect("home")
    return render(request, "core/appointments_adopter.html")


# ---------- OWNER ----------
@login_required
def owner_add_pet(request):
    if request.method == "POST":
        Pet.objects.create(
            name=request.POST.get("name"),
            category=request.POST.get("category"),
            description=request.POST.get("description", ""),
            image=request.FILES.get("image"),
            added_by=request.user,
            is_available=False,
        )
        return redirect("owner_pets")

    return render(request, "core/owner_add_pet.html")


@login_required
def owner_adoptions(request):
    requests = AdoptionRequest.objects.filter(
        owned_pet__owner=request.user
    )
    return render(
        request,
        "core/owner_adoptions.html",
        {"requests": requests}
    )


@login_required
def owner_appointments(request):
    return render(request, "core/owner_appointments.html")


@login_required
def owner_profile(request):
    return render(request, "core/owner_profile.html")


@login_required
def owned_pet_detail(request, pet_id):
    pet = get_object_or_404(OwnedPet, id=pet_id)
    return render(
        request,
        "core/owned_pet_detail.html",
        {"pet": pet}
    )


@login_required
def owner_approve_request(request, req_id):
    req = get_object_or_404(
        AdoptionRequest,
        id=req_id,
        owned_pet__owner=request.user
    )
    req.status = "approved"
    req.save()

    req.owned_pet.is_available = False
    req.owned_pet.save()

    return redirect("owner_adoptions")


@login_required
def owner_reject_request(request, req_id):
    req = get_object_or_404(
        AdoptionRequest,
        id=req_id,
        owned_pet__owner=request.user
    )
    req.status = "declined"
    req.save()

    return redirect("owner_adoptions")


# ---------- SHELTER ----------
def shelter_signup(request):
    return render(request, "core/shelter_signup.html")


@login_required
def shelter_profile(request):
    return render(request, "core/shelter_profile.html")


@login_required
def shelter_edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, added_by=request.user)
    return render(
        request,
        "core/shelter_edit_pet.html",
        {"pet": pet}
    )


@login_required
def shelter_delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, added_by=request.user)
    pet.delete()
    return redirect("shelter_pets")


@login_required
def shelter_adoptions(request):
    requests = AdoptionRequest.objects.filter(
        pet__added_by=request.user
    )
    return render(
        request,
        "core/shelter_adoptions.html",
        {"requests": requests}
    )


@login_required
def approve_request(request, req_id):
    req = get_object_or_404(
        AdoptionRequest,
        id=req_id,
        pet__added_by=request.user
    )
    req.status = "approved"
    req.save()

    req.pet.is_available = False
    req.pet.save()

    return redirect("shelter_adoptions")


@login_required
def decline_request(request, req_id):
    req = get_object_or_404(
        AdoptionRequest,
        id=req_id,
        pet__added_by=request.user
    )
    req.status = "declined"
    req.save()

    return redirect("shelter_adoptions")


# ---------- MISC ----------
@login_required
def chat(request):
    return render(request, "core/chat.html")


@login_required
def payment(request):
    return render(request, "core/payment.html")


# ---------- SUPER ADMIN ----------
@login_required
def superadmin_orders(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request, "core/admin/orders.html")


@login_required
def superadmin_analytics(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request, "core/admin/analytics.html")
@login_required
def adopter_favorites(request):
    if request.user.role != "adopter":
        return redirect("home")
    return render(request, "core/favorites_adopter.html")
@login_required
def send_owner_adoption_request(request, pet_id):
    """
    Wrapper to support existing URL:
    /adopt/owner/<pet_id>/
    """
    if request.user.role != "adopter":
        return redirect("home")

    owned_pet = get_object_or_404(
        OwnedPet,
        id=pet_id,
        is_available=True
    )

    AdoptionRequest.objects.get_or_create(
        adopter=request.user,
        owned_pet=owned_pet
    )

    return redirect("pets_list")
@login_required
def shelter_mark_available(request, pet_id):
    if request.user.role != "shelter":
        return redirect("home")

    pet = get_object_or_404(
        Pet,
        id=pet_id,
        added_by=request.user
    )

    pet.is_available = True
    pet.save()

    return redirect("shelter_pets")


@login_required
def shelter_mark_unavailable(request, pet_id):
    if request.user.role != "shelter":
        return redirect("home")

    pet = get_object_or_404(
        Pet,
        id=pet_id,
        added_by=request.user
    )

    pet.is_available = False
    pet.save()

    return redirect("shelter_pets")
