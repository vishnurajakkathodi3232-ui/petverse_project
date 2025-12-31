from django.shortcuts import render
from .models import Product, ProductCategory

from django.db.models import Q
from django.shortcuts import render
from .models import Product, ProductCategory
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def product_list(request):
    categories = ProductCategory.objects.filter(is_active=True)

    # Get filters from URL
    search_query = request.GET.get("q", "")
    category_id = request.GET.get("category")

    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    )

    # Search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Category filter
    if category_id:
        products = products.filter(category_id=category_id)

    products = products.select_related("category")

    context = {
        "categories": categories,
        "products": products,
        "search_query": search_query,
        "active_category": category_id,
    }

    return render(request, "shop/product_list.html", context)

from django.shortcuts import render, get_object_or_404
from .models import Product


def product_detail(request, pk):
    """
    Product detail page.
    Shows only active products under active categories.
    """

    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
        category__is_active=True
    )

    context = {
        'product': product,
    }

    return render(request, 'shop/product_detail.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product


def _get_cart(session):
    """
    Returns cart from session.
    Cart structure (payment-ready):
    {
        product_id: {
            'name': str,
            'price': str,   # snapshot for payment safety
            'quantity': int
        }
    }
    """
    return session.get('cart', {})


def cart_add(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True
    )

    cart = _get_cart(request.session)

    product_id_str = str(product.id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),  # snapshot (important for payment)
            'quantity': 1,
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('shop:cart_detail')


def cart_remove(request, product_id):
    cart = _get_cart(request.session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('shop:cart_detail')


def cart_detail(request):
    cart = _get_cart(request.session)

    cart_items = []
    total_amount = 0

    for product_id, item in cart.items():
        subtotal = float(item['price']) * item['quantity']
        total_amount += subtotal

        cart_items.append({
            'product_id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }

    return render(request, 'shop/cart.html', context)
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem

@login_required
def checkout(request):
    """
    Converts session cart into an Order + OrderItems.
    Payment will be integrated after this step.
    """

    cart = request.session.get('cart')

    if not cart:
        return redirect('shop:cart_detail')

    total_amount = 0
    order_items = []

    for item in cart.values():
        subtotal = float(item['price']) * item['quantity']
        total_amount += subtotal

        order_items.append({
            'product_name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
        })

    # Create Order
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
        status='pending'
    )

    # Create Order Items
    for item in order_items:
        OrderItem.objects.create(
            order=order,
            product_name=item['product_name'],
            price=item['price'],
            quantity=item['quantity']
        )

    # Clear cart AFTER order creation
    del request.session['cart']
    request.session.modified = True

    context = {
        'order': order,
    }

    return redirect('shop:payment_page', order_id=order.id)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, Payment
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required
def payment_page(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status='pending'
    )

    # Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # Create Razorpay order (amount in paise)
    razorpay_order = client.order.create({
        "amount": int(order.total_amount * 100),  # ₹ → paise
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        "order": order,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": order.total_amount,
        "currency": "INR",
    }

    return render(request, "shop/payment.html", context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Order, Payment


from .utils_email import send_order_invoice_email
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Order, Payment
@csrf_exempt  # Razorpay may POST here later
@login_required
def payment_success(request, order_id):
    """
    Razorpay payment success (safe client-side confirmation)
    """

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Prevent duplicate processing
    if order.status == "paid":
        return render(request, "shop/payment_success.html", {"order": order})

    # Create or update payment safely
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "status": "paid",
            "payment_id": "RAZORPAY_TEST"
        }
    )

    if not created:
        payment.status = "paid"
        payment.save()

    # Mark order as paid
    order.status = "paid"
    order.save()

    # 📧 Send invoice email (SAFE MODE)
    send_order_invoice_email(order)

    return render(request, "shop/payment_success.html", {"order": order})

from django.contrib.auth.decorators import login_required
from .models import Order


@login_required
def my_orders(request):
    """
    Shows logged-in user's order history.
    """

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'orders': orders,
    }

    return render(request, 'shop/my_orders.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from .models import Order
from .utils import generate_invoice_pdf


@login_required
def download_invoice(request, order_id):
    """
    Allows user to download invoice PDF
    Only for PAID orders
    Only order owner can access
    """

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Allow invoice only for paid orders
    if order.status != "paid":
        return HttpResponseForbidden("Invoice available only after payment.")

    return generate_invoice_pdf(order)
