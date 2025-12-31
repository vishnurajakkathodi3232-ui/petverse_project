# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import Payment


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
from .models import Service
from itertools import chain
from .models import OwnedPet, Service
def home(request):
    # Show ALL pets on homepage
    pets = Pet.objects.all().order_by("-id")

    services = Service.objects.filter(is_active=True)

    owned_pets = []
    if request.user.is_authenticated:
        owned_pets = OwnedPet.objects.filter(owner=request.user)

    return render(request, "core/home.html", {
        "pets": pets,
        "owned_pets": owned_pets,
        "services": services,
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Appointment, ServiceAppointment, Service, OwnedPet
from .models import OwnedPet, AdoptionRequest, Service


def make_appointment(request):
    if request.method != "POST":
        return redirect("home")

    # ==================================================
    # CASE 1: Logged-in user → Service Appointment
    # ==================================================
    if request.user.is_authenticated:

        if request.user.role not in ["adopter", "owner"]:
            messages.error(request, "You are not allowed to book services.")
            return redirect("home")

        pet_id = request.POST.get("pet_id")
        service_id = request.POST.get("service_id")
        date = request.POST.get("date")
        time = request.POST.get("time")
        notes = request.POST.get("message", "")

        # Basic validation
        if not pet_id or not service_id or not date or not time:
            messages.error(request, "Please fill all required fields.")
            return redirect(request.META.get("HTTP_REFERER", "home"))

        # Ownership validation (STRICT)
        owned_pet = get_object_or_404(
            OwnedPet,
            id=pet_id,
            owner=request.user
        )

        # Active service validation
        service = get_object_or_404(
            Service,
            id=service_id,
            is_active=True
        )

        # ✅ SAVE (now safe)
        appointment = ServiceAppointment.objects.create(
            user=request.user,
            owned_pet=owned_pet,
            service=service,
            appointment_date=date,
            appointment_time=time,
            notes=notes,
            status="pending"
        )

# 🔹 CREATE PAYMENT (AUTO)
        Payment.objects.create(
            user=request.user,
            payment_for="appointment",
            amount=service.price,
            appointment=appointment,
            status="pending"
        )


        messages.success(
            request,
            f"Appointment booked for {owned_pet.pet.name}."
        )
        return redirect("appointment_payment_review", appointment.id)


    # ==================================================
    # CASE 2: Public Appointment (Old behavior)
    # ==================================================
    Appointment.objects.create(
        name=request.POST.get("name"),
        email=request.POST.get("email"),
        date=request.POST.get("date"),
        service=request.POST.get("service"),
        phone=request.POST.get("phone"),
        message=request.POST.get("message"),
    )

    messages.success(request, "Appointment request submitted.")
    return redirect("home")

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
            return redirect("dashboard")

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

    owner_pets = OwnedPet.objects.filter(
        is_listed_for_adoption=True
    ).select_related("pet")

    combined = []

    for pet in shelter_pets:
        combined.append({
            "id": pet.id,
            "name": pet.name,
            "category": pet.category,
            "image": pet.image,
            "source": "shelter",
        })

    for owned in owner_pets:
        combined.append({
            "id": owned.id,
            "name": owned.pet.name,
            "category": owned.pet.category,
            "image": owned.pet.image,
            "source": "owner",
        })

    return render(
        request,
        "core/pets_list.html",
        {"pets": combined}
    )

@login_required
def send_adoption_request(request, pet_id):
    # Only adopters can send adoption requests
    if request.user.role != "adopter":
        return redirect("home")

    # Shelter pet must be AVAILABLE
    pet = get_object_or_404(
        Pet,
        id=pet_id,
        is_available=True
    )

    # Prevent duplicate requests
    if AdoptionRequest.objects.filter(
        adopter=request.user,
        pet=pet
    ).exists():
        return render(
            request,
            "core/request_status.html",
            {"message": "You have already requested this pet."}
        )

    if request.method == "POST":
        message = request.POST.get("message")

        AdoptionRequest.objects.create(
            adopter=request.user,
            pet=pet,
            message=message
        )

        return render(
            request,
            "core/request_status.html",
            {"message": "Adoption request sent successfully!"}
        )

    return render(
        request,
        "core/send_adoption_request.html",
        {"pet": pet}
    )

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
    owned_pet.is_listed_for_adoption = True
    owned_pet.save()
    return redirect("owner_pets")


@login_required
def owner_unlist_pet(request, pet_id):
    owned_pet = get_object_or_404(
        OwnedPet,
        id=pet_id,
        owner=request.user
    )
    owned_pet.is_listed_for_adoption = False
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

    appointments = ServiceAppointment.objects.filter(
        user=request.user
    ).select_related(
        "owned_pet__pet",
        "service"
    ).order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "core/adopter/appointments.html",
        {"appointments": appointments}
    )
# ---------- OWNER ----------
@login_required
def owner_add_pet(request):
    if not getattr(request.user, "has_pet", False):
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        pet_type = (
            request.POST.get("pet_type")
            or request.POST.get("category")
            or "Unknown"
        )
        image = request.FILES.get("image")
        description = request.POST.get("description", "Owner added pet")

        pet = Pet.objects.create(
            name=name,
            category=pet_type,
            description=description,
            image=image,
            is_available=False,
            added_by=request.user
        )

        OwnedPet.objects.create(
            owner=request.user,
            pet=pet
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


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ServiceAppointment

@login_required
def owner_appointments(request):
    if request.user.role != "owner":
        return redirect("home")

    appointments = ServiceAppointment.objects.filter(
        owned_pet__owner=request.user
    ).select_related(
        "owned_pet__pet",
        "service"
    ).order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "core/owner_appointments.html",
        {
            "appointments": appointments
        }
    )


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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Payment

@login_required
def payment_review(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user,
        status="pending"
    )

    return render(request, "core/payment_review.html", {
        "payment": payment
    })

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user,
        status="paid"
    )

    return render(request, "core/payment_success.html", {
        "payment": payment
    })
@login_required
def payment_history(request):
    user = request.user

    payments_made = Payment.objects.filter(
        user=user,
        status="paid"
    ).order_by("-created_at")

    payments_received = Payment.objects.none()

    # Owner / Shelter earnings (only adoption payments)
    if user.role in ["owner", "shelter"]:
        payments_received = Payment.objects.filter(
            receiver=user,
            status="paid"
        ).order_by("-created_at")

    return render(request, "core/payment_history.html", {
        "payments_made": payments_made,
        "payments_received": payments_received,
    })


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
    # Only adopters can send requests
    if request.user.role != "adopter":
        return redirect("home")

    owned_pet = get_object_or_404(
        OwnedPet,
        id=pet_id,
        is_listed_for_adoption=True
    )

    # Prevent duplicate requests
    if AdoptionRequest.objects.filter(
        adopter=request.user,
        owned_pet=owned_pet
    ).exists():
        return render(
            request,
            "core/request_status.html",
            {"message": "You already requested this pet."}
        )

    if request.method == "POST":
        message = request.POST.get("message")

        AdoptionRequest.objects.create(
            adopter=request.user,
            owned_pet=owned_pet,
            message=message
        )

        return render(
            request,
            "core/request_status.html",
            {"message": "Adoption request sent successfully!"}
        )

    return render(
        request,
        "core/send_adoption_request.html",
        {"pet": owned_pet.pet}
    )

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
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_redirect(request):
    user = request.user

    # Super Admin
    if user.is_superuser:
        return redirect("superadmin_dashboard")

    # Shelter
    if getattr(user, "role", None) == "shelter":
        return redirect("shelter_dashboard")

    # Owner
    if getattr(user, "role", None) == "owner" or getattr(user, "has_pet", False):
        return redirect("owner_dashboard")

    # Adopter
    if getattr(user, "role", None) == "adopter":
        return redirect("adopter_dashboard")

    # Fallback
    return redirect("home")
from .models import ServiceAppointment


@login_required
def my_service_appointments(request):
    appointments = ServiceAppointment.objects.filter(
        user=request.user
    ).select_related(
        "owned_pet__pet",
        "service"
    ).order_by("-created_at")

    return render(
        request,
        "core/my_service_appointments.html",
        {"appointments": appointments}
    )
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Service, OwnedPet

@login_required
def appointment_page(request):
    # Only adopter & owner allowed
    if request.user.role not in ["adopter", "owner"]:
        return redirect("home")

    services = Service.objects.filter(is_active=True)

    pets = []
    if request.user.role == "owner":
        pets = OwnedPet.objects.filter(owner=request.user)

    # adopter gets NO pets here (custom pet handled in template later)

    return render(
        request,
        "core/appointment_page.html",
        {
            "services": services,
            "pets": pets,
        }
    )

from .models import ChatRoom, ChatMessage


@login_required
def chat_room(request,  req_id):
    adoption_request = get_object_or_404(
        AdoptionRequest,
        id= req_id
    )

    # Permission check
    if request.user not in [
        adoption_request.adopter,
        getattr(adoption_request, "owned_pet", None) and adoption_request.owned_pet.owner,
        adoption_request.pet and adoption_request.pet.added_by
    ]:
        return redirect("dashboard")

    room, created = ChatRoom.objects.get_or_create(
        adoption_request=adoption_request
    )

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            ChatMessage.objects.create(
                room=room,
                sender=request.user,
                message=message
            )

    messages = room.messages.select_related("sender").order_by("created_at")

    return render(request, "core/chat_room.html", {
        "room": room,
        "messages": messages,
        "request_obj": adoption_request
    })
from .models import ChatRoom, AdoptionRequest
from django.db.models import Q

@login_required
def chat_inbox(request):
    rooms = ChatRoom.objects.filter(
        Q(adoption_request__adopter=request.user) |
        Q(adoption_request__pet__added_by=request.user) |
        Q(adoption_request__owned_pet__owner=request.user)
    ).select_related("adoption_request")

    return render(request, "core/chat_inbox.html", {
        "rooms": rooms
    })

from .utils import generate_payment_receipt
from .models import Payment


@login_required
def download_payment_receipt(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user
    )

    if payment.status != "paid":
        return redirect("dashboard")

    return generate_payment_receipt(payment)
# core/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from .models import ServiceAppointment
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ServiceAppointment

@login_required
def appointment_payment_review(request, appointment_id):
    appointment = get_object_or_404(
        ServiceAppointment,
        id=appointment_id,
        user=request.user
    )

    if appointment.status == "confirmed":
        return redirect("adopter_appointments")

    base_price = appointment.service.price
    surcharge_amount = Decimal("0.00")

    if request.user.role == "adopter":
        surcharge_amount = base_price * Decimal("0.15")

    final_amount = base_price + surcharge_amount

    return render(
        request,
        "core/payment_review.html",
        {
            "appointment": appointment,
            "base_price": base_price,
            "surcharge_amount": surcharge_amount,
            "final_amount": final_amount,
            "surcharge_applied": surcharge_amount > 0,
        }
    )

import razorpay
from django.conf import settings
from decimal import Decimal

@login_required
def appointment_payment_gateway(request, appointment_id):
    appointment = get_object_or_404(
        ServiceAppointment,
        id=appointment_id,
        user=request.user
    )

    payment = get_object_or_404(
        Payment,
        appointment=appointment,
        status="pending"
    )

    base_price = appointment.service.price
    amount = base_price

    if request.user.role == "adopter":
        amount = base_price + (base_price * Decimal("0.15"))

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(amount * 100),  # paise
        "currency": "INR",
        "payment_capture": 1,
    })

    payment.razorpay_order_id = razorpay_order["id"]
    payment.amount = amount
    payment.save()

    return render(request, "core/appointments/payment_gateway.html", {
        "appointment": appointment,
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "amount": int(amount * 100),
    })
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .models import Payment
from .utils import send_appointment_payment_receipt



@csrf_exempt
@login_required
def appointment_payment_success(request, payment_id):
    """
    Razorpay verified appointment payment success
    """

    if request.method != "POST":
        return redirect("adopter_appointments")

    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user,
        payment_for="appointment"
    )

    appointment = payment.appointment

    # Prevent duplicate processing
    if appointment.status == "confirmed":
        return redirect("adopter_appointments")

    # Razorpay response values
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    # 🛑 Safety check
    if razorpay_order_id != payment.razorpay_order_id:
        payment.status = "failed"
        payment.save()
        return render(
            request,
            "core/appointments/payment_failed.html",
            {"appointment": appointment}
        )

    # Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        # 🔐 Signature verification
        client.utility.verify_payment_signature({
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        payment.status = "failed"
        payment.save()

        return render(
            request,
            "core/appointments/payment_failed.html",
            {"appointment": appointment}
        )

    # ✅ VERIFIED PAYMENT
    payment.status = "paid"
    payment.payment_id = razorpay_payment_id
    payment.save()

    appointment.status = "confirmed"
    appointment.save()

    # 📧 SEND EMAIL RECEIPT
    send_appointment_payment_receipt(payment)

    return render(
        request,
        "core/payment_success.html",
        {
            "appointment": appointment,
            "payment": payment
        }
    )
