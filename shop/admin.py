from django.contrib import admin
from .models import ProductCategory, Product


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')
    ordering = ('name',)
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username')
    ordering = ('-created_at',)

    inlines = [OrderItemInline]

    readonly_fields = ('user', 'total_amount', 'created_at')

    def has_add_permission(self, request):
        return False  # Orders must be created via checkout only

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent accidental deletion
