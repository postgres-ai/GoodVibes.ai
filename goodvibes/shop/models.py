from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class Product(models.Model):
    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = []


class Customer(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Functional index used by case-insensitive lookups (kept - likely used)
            models.Index(Lower("email"), name="idx_customer_email_lower"),
        ]


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            # Composite index used by our hot path queries (kept - actively used)
            models.Index(fields=["customer", "created_at"], name="idx_order_customer_created_at"),
            # Partial index for non-cancelled orders (kept - workload favors this)
            models.Index(
                fields=["cancelled_at"], name="idx_order_cancelled_partial", condition=Q(cancelled_at__isnull=True)
            ),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            # Used by joins/filters that start with order (kept - actively used)
            models.Index(fields=["order", "product"], name="idx_orderitem_order_product"),
            # Single-column shadowed by composite (kept - may be used for order-only queries)
            models.Index(fields=["order"], name="idx_orderitem_order_only"),
        ]


