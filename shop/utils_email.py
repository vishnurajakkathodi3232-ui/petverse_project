from django.core.mail import EmailMessage
from django.conf import settings
from .utils import generate_invoice_pdf


def send_order_invoice_email(order):
    """
    Sends invoice email with PDF attachment to buyer
    """

    subject = f"PetVerse Invoice – Order #{order.id}"

    body = f"""
Hi {order.user.get_full_name() or order.user.username},

Thank you for shopping with PetVerse 🐾

Order ID: {order.id}
Amount Paid: ₹ {order.total_amount}

Your invoice is attached with this email.

Regards,
PetVerse Team
"""

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.user.email],
    )

    # Attach PDF
    pdf_response = generate_invoice_pdf(order)
    email.attach(
        filename=f"invoice_{order.id}.pdf",
        content=pdf_response.content,
        mimetype="application/pdf",
    )

    email.send(fail_silently=True)
