from django.shortcuts import render
from .models import Product, ProductCategory


def product_list(request):
    """
    Public product listing page.
    Shows only active products under active categories.
    """

    categories = ProductCategory.objects.filter(is_active=True)

    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).select_related('category')

    context = {
        'categories': categories,
        'products': products,
    }

    return render(request, 'shop/product_list.html', context)
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
        # No cart → redirect safely
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

    return render(request, 'shop/checkout_success.html', context)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, Payment


@login_required
def payment_page(request, order_id):
    """
    Displays payment page (mock gateway).
    """

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status='pending'
    )

    # Create payment record if not exists
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={'status': 'initiated'}
    )

    context = {
        'order': order,
        'payment': payment,
    }

    return render(request, 'shop/payment.html', context)


@login_required
def payment_success(request, order_id):
    """
    Mock payment success callback.
    """

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    payment = get_object_or_404(Payment, order=order)

    # Update payment & order status
    payment.status = 'success'
    payment.payment_id = f"MOCKPAY-{order.id}"
    payment.save()

    order.status = 'paid'
    order.save()

    return render(request, 'shop/payment_success.html', {'order': order})
