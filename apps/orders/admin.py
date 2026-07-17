from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'payment_method', 'payment_status', 'status', 'date_created')
    list_filter = ('status', 'payment_method', 'payment_status')
    search_fields = ('order_number', 'user__email', 'shipping_full_name')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'subtotal', 'total')