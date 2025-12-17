import random
import time
from typing import List

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from goodvibes.shop.models import Customer, Order, OrderItem, Product


class Command(BaseCommand):
    help = (
        "Generate index bloat by creating churn (INSERT/UPDATE/DELETE) on indexed tables. "
        "This is intentionally write-heavy; unlike simulate_load, it can create bloat."
    )

    def add_arguments(self, parser):
        parser.add_argument("--seconds", type=int, default=60, help="Duration to run churn")
        parser.add_argument(
            "--items-per-order",
            type=int,
            default=5,
            help="How many OrderItem rows to create per new Order",
        )
        parser.add_argument(
            "--delete-ratio",
            type=float,
            default=0.9,
            help="Probability (0..1) to delete a just-created order (cascades to OrderItems)",
        )
        parser.add_argument(
            "--toggle-cancel-ratio",
            type=float,
            default=0.5,
            help="Probability (0..1) to toggle cancelled_at on an existing order (updates indexed column)",
        )
        parser.add_argument("--sleep-ms", type=int, default=0, help="Optional sleep between ops in ms")
        parser.add_argument("--seed", type=int, default=123, help="PRNG seed")

    def handle(self, *args, **options):
        seconds: int = max(1, int(options["seconds"]))
        items_per_order: int = max(1, int(options["items_per_order"]))
        delete_ratio: float = min(1.0, max(0.0, float(options["delete_ratio"])))
        toggle_cancel_ratio: float = min(1.0, max(0.0, float(options["toggle_cancel_ratio"])))
        sleep_ms: int = max(0, int(options["sleep_ms"]))
        seed: int = int(options["seed"])

        random.seed(seed)
        self.stdout.write(
            self.style.SUCCESS(
                "Generating bloat for "
                f"{seconds}s (items/order={items_per_order}, delete_ratio={delete_ratio}, "
                f"toggle_cancel_ratio={toggle_cancel_ratio}, sleep={sleep_ms}ms)"
            )
        )

        # Preload ids to avoid adding extra read load beyond what's needed.
        product_ids: List[int] = list(Product.objects.values_list("id", flat=True)[:10000])
        customer_ids: List[int] = list(Customer.objects.values_list("id", flat=True)[:10000])
        existing_order_ids: List[int] = list(Order.objects.values_list("id", flat=True)[:20000])

        if not (product_ids and customer_ids):
            self.stdout.write(self.style.ERROR("Insufficient data; run seed_demo_data first."))
            return

        end_at = time.time() + seconds
        ops = 0
        created_orders = 0
        deleted_orders = 0
        toggled_orders = 0

        while time.time() < end_at:
            # 1) UPDATE churn on indexed column: cancelled_at (affects both full and partial indexes)
            if existing_order_ids and random.random() < toggle_cancel_ratio:
                oid = random.choice(existing_order_ids)
                # Flip between NULL and NOW(); each flip updates the cancelled_at indexes.
                updated = Order.objects.filter(id=oid, cancelled_at__isnull=True).update(cancelled_at=timezone.now())
                if not updated:
                    Order.objects.filter(id=oid, cancelled_at__isnull=False).update(cancelled_at=None)
                toggled_orders += 1
                ops += 1
            else:
                # 2) INSERT+DELETE churn on Order / OrderItem to bloat their indexes (esp. OrderItem composites).
                cid = random.choice(customer_ids)
                with transaction.atomic():
                    order = Order.objects.create(customer_id=cid)
                    created_orders += 1

                    items = [
                        OrderItem(
                            order=order,
                            product_id=random.choice(product_ids),
                            quantity=random.randint(1, 5),
                        )
                        for _ in range(items_per_order)
                    ]
                    OrderItem.objects.bulk_create(items, batch_size=max(100, items_per_order))

                    # Keep a pool of ids for the toggle path (even if we delete many of them).
                    existing_order_ids.append(order.id)
                    if len(existing_order_ids) > 20000:
                        existing_order_ids = existing_order_ids[-20000:]

                    if random.random() < delete_ratio:
                        # Deleting Order cascades to OrderItems; both tables' indexes accumulate dead tuples.
                        order.delete()
                        deleted_orders += 1

                ops += 1

            if sleep_ms:
                time.sleep(sleep_ms / 1000.0)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. ops={ops}, created_orders={created_orders}, deleted_orders={deleted_orders}, toggled_orders={toggled_orders}"
            )
        )


