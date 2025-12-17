import math
import random
import string
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

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
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=50000,
            help="Number of rows to generate per bulk_create chunk",
        )
        parser.add_argument(
            "--no-transaction",
            action="store_true",
            help="Do not wrap the entire seeding in a single transaction (recommended for very large seeds)",
        )
        parser.add_argument(
            "--txn-per-batch",
            action="store_true",
            help="Wrap each generation batch in its own transaction (improves throughput vs autocommit per statement)",
        )

    def handle(self, *args, **options):
        random.seed(42)
        scale = max(1, int(options["scale"]))
        chunk_size = max(1000, int(options["chunk_size"]))
        use_single_txn = not bool(options["no_transaction"])
        txn_per_batch = bool(options["txn_per_batch"])
        # If per-batch transactions are requested, do not use a single huge transaction
        if txn_per_batch:
            use_single_txn = False

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

        @contextmanager
        def _maybe_batch_atomic():
            if txn_per_batch:
                with transaction.atomic():
                    yield
            else:
                yield

        def _seed_impl():
            # Products (chunked)
            existing = Product.objects.count()
            to_create = max(0, num_products - existing)
            if to_create:
                self.stdout.write(self.style.SUCCESS(f"Creating {to_create} products (existing={existing})"))
                categories = ["books", "games", "toys", "tools", "garden", "kitchen"]
                created = 0
                # Use sequential indices starting after existing for stable names
                next_idx = existing
                while created < to_create:
                    batch = []
                    batch_n = min(chunk_size, to_create - created)
                    for i in range(batch_n):
                        idx = next_idx + i
                        batch.append(
                            Product(
                                sku=_random_sku(),
                                name=_random_name("Product", idx),
                                category=random.choice(categories),
                                is_active=random.random() > 0.05,
                            )
                        )
                    with _maybe_batch_atomic():
                        Product.objects.bulk_create(batch, batch_size=1000, ignore_conflicts=True)
                    created += batch_n
                    next_idx += batch_n
            self.stdout.write(self.style.SUCCESS(f"Products: {Product.objects.count()}"))

            # Customers (chunked)
            existing = Customer.objects.count()
            to_create = max(0, num_customers - existing)
            if to_create:
                self.stdout.write(self.style.SUCCESS(f"Creating {to_create} customers (existing={existing})"))
                created = 0
                next_idx = existing
                while created < to_create:
                    batch = []
                    batch_n = min(chunk_size, to_create - created)
                    for i in range(batch_n):
                        idx = next_idx + i
                        batch.append(Customer(email=_random_email(idx), full_name=_random_name("Customer", idx)))
                    with _maybe_batch_atomic():
                        Customer.objects.bulk_create(batch, batch_size=1000, ignore_conflicts=True)
                    created += batch_n
                    next_idx += batch_n
            self.stdout.write(self.style.SUCCESS(f"Customers: {Customer.objects.count()}"))

            # Orders (chunked) + generate items for newly created orders to avoid scanning all order ids
            existing_orders = Order.objects.count()
            to_create_orders = max(0, num_orders - existing_orders)
            self.stdout.write(self.style.SUCCESS(f"Creating {to_create_orders} orders (existing={existing_orders})"))
            if to_create_orders:
                # Preload a sample of customer ids and product ids to avoid materializing huge arrays
                customer_ids = list(Customer.objects.values_list("id", flat=True)[:100000])
                if not customer_ids:
                    self.stdout.write(self.style.ERROR("No customers present; aborting."))
                    return
                # For products, keep a moderate sample to randomize item product selection
                product_sample = list(Product.objects.values_list("id", flat=True)[:200000])
                if not product_sample:
                    self.stdout.write(self.style.ERROR("No products present; aborting."))
                    return
                now = datetime.now(timezone.utc)
                created_orders_total = 0
                while created_orders_total < to_create_orders:
                    batch_n = min(chunk_size, to_create_orders - created_orders_total)
                    order_batch = []
                    for _ in range(batch_n):
                        cust_id = random.choice(customer_ids)
                        created_at = now - timedelta(days=random.randint(0, 365), seconds=random.randint(0, 86400))
                        cancelled_at = None
                        # ~10% cancelled
                        if random.random() < 0.1:
                            cancelled_at = created_at + timedelta(hours=random.randint(1, 72))
                            # Sometimes None to hit partial index
                            if random.random() < 0.5:
                                cancelled_at = None
                        order_batch.append(Order(customer_id=cust_id, created_at=created_at, cancelled_at=cancelled_at))
                    with _maybe_batch_atomic():
                        created_orders = Order.objects.bulk_create(order_batch, batch_size=1000)

                        # Items for the newly created orders
                        items_batch = []
                        for o in created_orders:
                            # ~avg_items_per_order items per order, but vary between 1..(2*avg-1)
                            num_items_for_order = max(1, int(random.gauss(avg_items_per_order, 1)))
                            for _ in range(num_items_for_order):
                                items_batch.append(
                                    OrderItem(
                                        order_id=o.id,
                                        product_id=random.choice(product_sample),
                                        quantity=random.randint(1, 5),
                                    )
                                )
                        if items_batch:
                            # larger batch size is fine for items
                            OrderItem.objects.bulk_create(items_batch, batch_size=5000)

                    created_orders_total += len(created_orders)
                    self.stdout.write(self.style.SUCCESS(f"Orders so far: {existing_orders + created_orders_total}"))

            self.stdout.write(self.style.SUCCESS("Seeding completed."))

        if use_single_txn:
            with transaction.atomic():
                _seed_impl()
        else:
            _seed_impl()


