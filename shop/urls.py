from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # Payment (mock / skeleton)
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
]
