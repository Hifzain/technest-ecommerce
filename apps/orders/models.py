from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.products.models import Product
from apps.accounts.models import Address
import random
import string


def generate_order_number():
    date_part = timezone.now().strftime('%Y%m%d')
    rand_part = ''.join(random.choices(string.digits, k=5))
    return f"ORD-{date_part}-{rand_part}"


class Order(models.Model):
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Processing'),
        (2, 'Shipped'),
        (3, 'Delivered'),
        (4, 'Cancelled'),
    )
    PAYMENT_METHOD_CHOICES = (
        (0, 'Cash on Delivery'),
        (1, 'Card (Stripe)'),
    )
    PAYMENT_STATUS_CHOICES = (
        (0, 'Unpaid'),
        (1, 'Paid'),
        (2, 'Refunded'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=30, unique=True, blank=True)

    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='orders')

    # Snapshot the address at time of order (in case user edits/deletes it later)
    shipping_full_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=20)
    shipping_address_line = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.PositiveSmallIntegerField(choices=PAYMENT_METHOD_CHOICES, default=0)
    payment_status = models.PositiveSmallIntegerField(choices=PAYMENT_STATUS_CHOICES, default=0)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)

    notes = models.TextField(blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')

    # Snapshot product details at time of purchase (prices/names can change later)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
