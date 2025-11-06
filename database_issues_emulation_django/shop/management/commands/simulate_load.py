import random
import time
from typing import List

from django.core.management.base import BaseCommand

from goodvibes.shop.models import Customer, Order, OrderItem, Product


class Command(BaseCommand):
    help = "Simulate a biased workload to exercise only a subset of indexes."

    def add_arguments(self, parser):
        parser.add_argument("--seconds", type=int, default=60, help="Duration to run load")
        parser.add_argument("--sleep-ms", type=int, default=0, help="Optional sleep between ops in ms")

    def handle(self, *args, **options):
        seconds: int = max(1, int(options["seconds"]))
        sleep_ms: int = max(0, int(options["sleep_ms"]))

        random.seed(123)
        self.stdout.write(self.style.SUCCESS(f"Simulating load for {seconds}s (sleep {sleep_ms}ms)"))

        # Preload ids/keys to avoid extra queries
        product_skus: List[str] = list(Product.objects.values_list("sku", flat=True)[:10000])
        customer_ids: List[int] = list(Customer.objects.values_list("id", flat=True)[:10000])
        customer_emails: List[str] = list(Customer.objects.values_list("email", flat=True)[:10000])
        order_ids: List[int] = list(Order.objects.values_list("id", flat=True)[:20000])

        if not (product_skus and customer_ids and customer_emails and order_ids):
            self.stdout.write(self.style.ERROR("Insufficient data; run seed_demo_data first."))
            return

        end_at = time.time() + seconds
        ops = 0

        while time.time() < end_at:
            r = random.random()
            try:
                if r < 0.3:
                    # Product by SKU (uses implicit unique index; leaves duplicate non-unique unused)
                    sku = random.choice(product_skus)
                    Product.objects.only("id").get(sku=sku)
                elif r < 0.55:
                    # Customer by case-insensitive email (uses functional lower(email) index)
                    email = random.choice(customer_emails)
                    Customer.objects.only("id").get(email__iexact=email)
                elif r < 0.8:
                    # Recent orders for a customer (uses composite (customer, created_at))
                    cid = random.choice(customer_ids)
                    list(Order.objects.filter(customer_id=cid).order_by("-created_at").only("id")[:50])
                elif r < 0.95:
                    # Order items by order (uses (order, product) or (order))
                    oid = random.choice(order_ids)
                    list(OrderItem.objects.filter(order_id=oid).only("id")[:100])
                else:
                    # Cancelled filter with isnull True (planner should use partial index)
                    list(Order.objects.filter(cancelled_at__isnull=True).order_by("created_at").only("id")[:50])
            except Exception:
                # Ignore transient misses
                pass

            ops += 1
            if sleep_ms:
                time.sleep(max(0, sleep_ms) / 1000.0)

        self.stdout.write(self.style.SUCCESS(f"Completed {ops} operations."))


