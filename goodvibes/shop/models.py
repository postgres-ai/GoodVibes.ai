from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Indexes removed in migration 0004 - see H002 unused indexes issue
        # https://console.postgres.ai/goodvibes-ai/issues/019b3336-fb12-7072-b792-3233ffbcd699
        pass


class Customer(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Indexes removed in migration 0004 - see H002 unused indexes issue
        # https://console.postgres.ai/goodvibes-ai/issues/019b3336-fb12-7072-b792-3233ffbcd699
        pass


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Indexes removed in migration 0004 - see H002 unused indexes issue
        # https://console.postgres.ai/goodvibes-ai/issues/019b3336-fb12-7072-b792-3233ffbcd699
        pass


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Indexes removed in migration 0004 - see H002 unused indexes issue
        # https://console.postgres.ai/goodvibes-ai/issues/019b3336-fb12-7072-b792-3233ffbcd699
        pass


