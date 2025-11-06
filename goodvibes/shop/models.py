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
        indexes = [
            # Redundant duplicate alongside the implicit unique index
            models.Index(fields=["sku"], name="idx_product_sku_nonunique"),
            # Low-selectivity index (often not used)
            models.Index(fields=["is_active"], name="idx_product_is_active"),
            # Plain vs functional (we'll bias workload to use the functional)
            models.Index(fields=["name"], name="idx_product_name_plain"),
            models.Index(Lower("name"), name="idx_product_name_lower"),
        ]


class Customer(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Redundant duplicate alongside the implicit unique index
            models.Index(fields=["email"], name="idx_customer_email_plain"),
            # Functional index used by case-insensitive lookups
            models.Index(Lower("email"), name="idx_customer_email_lower"),
        ]


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            # Composite index used by our hot path queries
            models.Index(fields=["customer", "created_at"], name="idx_order_customer_created_at"),
            # Shadowed by the composite index for most queries
            models.Index(fields=["customer"], name="idx_order_customer_only"),
            # Full index vs partial; workload favors partial
            models.Index(fields=["cancelled_at"], name="idx_order_cancelled_full"),
            # INCLUDE variant (redundant coverage given the composite)
            models.Index(fields=["customer"], name="idx_order_cust_inc_created", include=["created_at"]),
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
            # Used by joins/filters that start with order
            models.Index(fields=["order", "product"], name="idx_orderitem_order_product"),
            # Reversed order (likely unused)
            models.Index(fields=["product", "order"], name="idx_oi_prod_order_bad"),
            # Single-column shadowed by composite
            models.Index(fields=["order"], name="idx_orderitem_order_only"),
        ]


