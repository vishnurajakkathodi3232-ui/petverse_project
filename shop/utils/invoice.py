from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils.timezone import now


def generate_invoice_pdf(order):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y, "PetVerse Invoice")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Order ID: #{order.id}")
    y -= 18

    c.drawString(50, y, f"Customer: {order.user.username}")
    y -= 18

    c.drawString(50, y, f"Date: {order.created_at.strftime('%d %b %Y')}")
    y -= 30

    # Table Header
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Product")
    c.drawString(280, y, "Qty")
    c.drawString(340, y, "Price")
    c.drawString(420, y, "Subtotal")
    y -= 15

    c.line(50, y, 550, y)
    y -= 20

    c.setFont("Helvetica", 11)

    for item in order.items.all():
        subtotal = item.quantity * float(item.price)

        c.drawString(50, y, item.product_name)
        c.drawString(280, y, str(item.quantity))
        c.drawString(340, y, f"₹ {item.price}")
        c.drawString(420, y, f"₹ {subtotal}")

        y -= 20

        if y < 80:
            c.showPage()
            y = height - 50

    # Total
    y -= 20
    c.line(50, y, 550, y)
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(340, y, "Total:")
    c.drawString(420, y, f"₹ {order.total_amount}")

    y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Thank you for shopping with PetVerse 🐾")

    c.showPage()
    c.save()

    return response
