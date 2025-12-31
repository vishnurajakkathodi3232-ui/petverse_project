from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


def generate_invoice_pdf(order):
    """
    Generates a PDF invoice for a Shop Order
    Returns HttpResponse (PDF download)
    """

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # =========================
    # HEADER
    # =========================
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(40, height - 50, "PetVerse")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 70, "Pet Products Invoice")

    pdf.setFont("Helvetica", 9)
    pdf.drawRightString(width - 40, height - 50, f"Invoice #: {order.id}")
    pdf.drawRightString(
        width - 40,
        height - 65,
        f"Date: {order.created_at.strftime('%d %b %Y')}"
    )

    # =========================
    # CUSTOMER DETAILS
    # =========================
    y = height - 120

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, "Billed To:")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        40,
        y - 15,
        order.user.get_full_name() or order.user.username
    )
    pdf.drawString(40, y - 30, order.user.email)

    # =========================
    # ORDER ITEMS TABLE
    # =========================
    table_y = y - 90

    data = [
        ["Product", "Price", "Qty", "Subtotal"]
    ]

    for item in order.items.all():
        subtotal = float(item.price) * item.quantity
        data.append([
            item.product_name,
            f"₹ {item.price}",
            str(item.quantity),
            f"₹ {subtotal}",
        ])

    # TOTAL ROW
    data.append([
        "",
        "",
        "Total",
        f"₹ {order.total_amount}"
    ])

    table = Table(
        data,
        colWidths=[3 * inch, 1.2 * inch, 0.8 * inch, 1.5 * inch]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.beige),
        ("FONT", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 40, table_y)

    # =========================
    # FOOTER
    # =========================
    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        40,
        50,
        "Thank you for shopping with PetVerse 🐾"
    )

    pdf.drawRightString(
        width - 40,
        50,
        "This is a system-generated invoice"
    )

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{order.id}.pdf"'
    )

    return response
