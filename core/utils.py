from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from datetime import datetime


def generate_payment_receipt(payment):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="PetVerse_Receipt_{payment.id}.pdf"'
    )

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "PetVerse - Payment Receipt")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Receipt ID: {payment.id}")
    y -= 20
    c.drawString(50, y, f"Date: {payment.created_at.strftime('%d %b %Y')}")
    y -= 30

    # User info
    c.drawString(50, y, f"Paid By: {payment.user.username}")
    y -= 20
    c.drawString(50, y, f"Payment Type: {payment.payment_for.title()}")
    y -= 20
    c.drawString(50, y, f"Amount Paid: ₹ {payment.amount}")
    y -= 30

    # Conditional details
    if payment.payment_for == "appointment" and payment.appointment:
        c.drawString(50, y, "Appointment Details:")
        y -= 20
        c.drawString(
            70, y,
            f"Service: {payment.appointment.service.name}"
        )
        y -= 20
        c.drawString(
            70, y,
            f"Pet: {payment.appointment.owned_pet.pet.name}"
        )

    elif payment.payment_for == "adoption" and payment.adoption_request:
        c.drawString(50, y, "Adoption Details:")
        y -= 20
        c.drawString(
            70, y,
            f"Pet: {payment.adoption_request.target_pet_name}"
        )
        y -= 20
        c.drawString(
            70, y,
            f"Type: {payment.adoption_request.adoption_type}"
        )

    elif payment.payment_for == "shop" and payment.order:
        c.drawString(50, y, "Shop Order Details:")
        y -= 20
        c.drawString(70, y, f"Order ID: {payment.order.id}")

    # Footer
    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(
        50, y,
        "Thank you for using PetVerse. This is a system-generated receipt."
    )

    c.showPage()
    c.save()

    return response
# core/utils.py

from django.core.mail import send_mail
from django.conf import settings
def send_appointment_payment_receipt(payment):
    subject = "PetVerse – Appointment Payment Successful"

    message = f"""
Hello {payment.user.first_name or payment.user.username},

Your appointment payment has been completed successfully.

Appointment ID: {payment.appointment.id}
Service: {payment.appointment.service.name}
Pet: {payment.appointment.owned_pet.pet.name}
Amount Paid: ₹ {payment.amount}

Thank you for choosing PetVerse 🐾
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payment.user.email],
        fail_silently=False
    )
