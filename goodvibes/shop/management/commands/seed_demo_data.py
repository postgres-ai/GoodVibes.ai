import math
import random
import string
from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand
from django.db import transaction

from goodvibes.shop.models import Customer, Order, OrderItem, Product


def _random_sku() -> str:
    return "SKU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def _random_email(i: int) -> str:
    return f"user{i}@example.com"


def _random_name(prefix: str, i: int) -> str:
    return f"{prefix} {i}"


class Command(BaseCommand):
    help = "Seed demo data for the shop app."

    def add_arguments(self, parser):
        parser.add_argument("--scale", type=int, default=1, help="Scale factor (multiplies base sizes)")

    def handle(self, *args, **options):
        random.seed(42)
        scale = max(1, int(options["scale"]))

        base_products = 1000
        base_customers = 500
        base_orders = 2000
        avg_items_per_order = 3

        num_products = base_products * scale
        num_customers = base_customers * scale
        num_orders = base_orders * scale
        num_items = num_orders * avg_items_per_order

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding with scale={scale}: products={num_products}, customers={num_customers}, orders={num_orders}, items~={num_items}"
            )
        )

        with transaction.atomic():
            # Products
            if Product.objects.count() < num_products:
                categories = ["books", "games", "toys", "tools", "garden", "kitchen"]
                products = []
                for i in range(num_products):
                    products.append(
                        Product(
                            sku=_random_sku(),
                            name=_random_name("Product", i),
                            category=random.choice(categories),
                            is_active=random.random() > 0.05,
                        )
                    )
                Product.objects.bulk_create(products, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Products: {Product.objects.count()}"))

            # Customers
            if Customer.objects.count() < num_customers:
                customers = [
                    Customer(email=_random_email(i), full_name=_random_name("Customer", i))
                    for i in range(num_customers)
                ]
                Customer.objects.bulk_create(customers, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Customers: {Customer.objects.count()}"))

            # Orders
            existing_orders = Order.objects.count()
            to_create = max(0, num_orders - existing_orders)
            self.stdout.write(self.style.SUCCESS(f"Creating {to_create} orders (existing={existing_orders})"))
            if to_create:
                all_customer_ids = list(Customer.objects.values_list("id", flat=True))
                if not all_customer_ids:
                    self.stdout.write(self.style.ERROR("No customers present; aborting."))
                    return
                now = datetime.now(timezone.utc)
                orders = []
                for i in range(to_create):
                    cust_id = random.choice(all_customer_ids)
                    created_at = now - timedelta(days=random.randint(0, 365), seconds=random.randint(0, 86400))
                    cancelled_at = None
                    # ~10% cancelled
                    if random.random() < 0.1:
                        cancelled_at = created_at + timedelta(hours=random.randint(1, 72))
                        # Sometimes None to hit partial index
                        if random.random() < 0.5:
                            cancelled_at = None
                    orders.append(Order(customer_id=cust_id, created_at=created_at, cancelled_at=cancelled_at))
                Order.objects.bulk_create(orders, batch_size=1000)

            # Order items
            created_order_ids = list(Order.objects.values_list("id", flat=True))
            product_ids = list(Product.objects.values_list("id", flat=True))
            if not created_order_ids or not product_ids:
                self.stdout.write(self.style.ERROR("No orders or products present; aborting items."))
                return
            # Heuristic: approximately 3 items per order
            target_items = len(created_order_ids) * avg_items_per_order
            existing_items = OrderItem.objects.count()
            to_create_items = max(0, target_items - existing_items)
            self.stdout.write(self.style.SUCCESS(f"Creating ~{to_create_items} order items"))
            if to_create_items:
                items = []
                for _ in range(to_create_items):
                    items.append(
                        OrderItem(
                            order_id=random.choice(created_order_ids),
                            product_id=random.choice(product_ids),
                            quantity=random.randint(1, 5),
                        )
                    )
                OrderItem.objects.bulk_create(items, batch_size=2000)

        self.stdout.write(self.style.SUCCESS("Seeding completed."))


