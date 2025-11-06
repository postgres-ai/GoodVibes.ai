from django.db import migrations, models
import django.db.models.deletion
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sku", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("category", models.CharField(max_length=64)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["sku"], name="idx_product_sku_nonunique"),
                    models.Index(fields=["is_active"], name="idx_product_is_active"),
                    models.Index(fields=["name"], name="idx_product_name_plain"),
                    models.Index(Lower("name"), name="idx_product_name_lower"),
                ]
            },
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("full_name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["email"], name="idx_customer_email_plain"),
                    models.Index(Lower("email"), name="idx_customer_email_lower"),
                ]
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
                (
                    "customer",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="shop.customer"),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["customer", "created_at"], name="idx_order_customer_created_at"),
                    models.Index(fields=["customer"], name="idx_order_customer_only"),
                    models.Index(fields=["cancelled_at"], name="idx_order_cancelled_full"),
                    models.Index(fields=["customer"], name="idx_order_cust_inc_created", include=["created_at"]),
                    models.Index(
                        fields=["cancelled_at"], name="idx_order_cancelled_partial", condition=models.Q(cancelled_at__isnull=True)
                    ),
                ]
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "order",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="shop.order"),
                ),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="shop.product"),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["order", "product"], name="idx_orderitem_order_product"),
                    models.Index(fields=["product", "order"], name="idx_oi_prod_order_bad"),
                    models.Index(fields=["order"], name="idx_orderitem_order_only"),
                ]
            },
        ),
    ]


