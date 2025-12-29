from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
from django.conf import settings


class Order(models.Model):
    """
    Represents a checkout order.
    Payment will be linked later.
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


class OrderItem(models.Model):
    """
    Snapshot of cart items at checkout time.
    """

    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    product_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"
class Payment(models.Model):
    """
    Stores payment information for an order.
    Gateway integration will be added later.
    """

    PAYMENT_STATUS = (
        ('initiated', 'Initiated'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    payment_id = models.CharField(max_length=100, blank=True, null=True)
    gateway = models.CharField(max_length=50, default='mock')
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='initiated'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"
