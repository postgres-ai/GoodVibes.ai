# Generated manually for H002 Unused indexes issue
# https://console.postgres.ai/goodvibes-ai/issues/019b3336-fb12-7072-b792-3233ffbcd699
#
# Drops 31 unused indexes consuming 19.2 GiB
# Statistics window: 36 days (since 2025-11-12)
#
# IMPORTANT: Each DROP INDEX CONCURRENTLY runs in its own transaction.
# This migration sets atomic = False as required by CONCURRENTLY operations.

from django.db import migrations
from django.contrib.postgres.operations import RemoveIndexConcurrently


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("shop", "0003_remove_orderitem_idx_orderitem_order_only_2"),
    ]

    operations = [
        # =====================================================================
        # shop_orderitem indexes (table: shop_orderitem)
        # =====================================================================
        # 2.94 GiB - Reversed column order, never used
        RemoveIndexConcurrently(
            model_name="orderitem",
            name="idx_oi_prod_order_bad",
        ),
        # 2.03 GiB - Composite index, shadowed by other indexes
        RemoveIndexConcurrently(
            model_name="orderitem",
            name="idx_orderitem_order_product",
        ),
        # 1.09 GiB - Single-column, shadowed by composite
        RemoveIndexConcurrently(
            model_name="orderitem",
            name="idx_orderitem_order_only",
        ),
        # 1.09 GiB - Django auto-created FK index
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.shop_orderitem_order_id_2f1b00cf;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_orderitem_order_id_2f1b00cf ON public.shop_orderitem USING btree (order_id);",
        ),
        # 628 MiB - Django auto-created FK index
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.shop_orderitem_product_id_48153f22;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_orderitem_product_id_48153f22 ON public.shop_orderitem USING btree (product_id);",
        ),

        # =====================================================================
        # shop_order indexes (table: shop_order)
        # =====================================================================
        # 1.10 GiB - Composite index
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_customer_created_at",
        ),
        # 1.09 GiB - INCLUDE variant, redundant
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_cust_inc_created",
        ),
        # 248 MiB - Shadowed by composite
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_customer_only",
        ),
        # 248 MiB - Django auto-created FK index
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.shop_order_customer_id_f638df20;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_order_customer_id_f638df20 ON public.shop_order USING btree (customer_id);",
        ),
        # 203 MiB - Full index, partial preferred
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_cancelled_full",
        ),
        # 164 MiB - Partial index
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_cancelled_partial",
        ),

        # =====================================================================
        # shop_customer indexes (table: shop_customer)
        # =====================================================================
        # 680 MiB - Functional index
        RemoveIndexConcurrently(
            model_name="customer",
            name="idx_customer_email_lower",
        ),
        # 680 MiB - Plain index, redundant with unique
        RemoveIndexConcurrently(
            model_name="customer",
            name="idx_customer_email_plain",
        ),
        # 680 MiB - Django auto-created pattern_ops index
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.shop_customer_email_d3fdf104_like;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_customer_email_d3fdf104_like ON public.shop_customer USING btree (email varchar_pattern_ops);",
        ),

        # =====================================================================
        # shop_product indexes (table: shop_product)
        # =====================================================================
        # 590 MiB - Functional index
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_name_lower",
        ),
        # 590 MiB - Plain index
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_name_plain",
        ),
        # 432 MiB - Redundant with unique index
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_sku_nonunique",
        ),
        # 432 MiB - Django auto-created pattern_ops index
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.shop_product_sku_20049d15_like;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_product_sku_20049d15_like ON public.shop_product USING btree (sku varchar_pattern_ops);",
        ),
        # 67.0 MiB - Low-selectivity index
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_is_active",
        ),

        # =====================================================================
        # order_items indexes (non-Django table)
        # =====================================================================
        # 2.64 GiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.order_items_order_sku_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_items_order_sku_idx ON public.order_items USING btree (order_id, product_sku);",
        ),
        # 449 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.order_items_sku_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_items_sku_idx ON public.order_items USING btree (product_sku);",
        ),

        # =====================================================================
        # orders indexes (non-Django table)
        # =====================================================================
        # 538 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.orders_customer_created_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_customer_created_idx ON public.orders USING btree (customer_id, created_at);",
        ),
        # 276 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.orders_customer_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_customer_idx ON public.orders USING btree (customer_id);",
        ),
        # 156 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.orders_status_city_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_status_city_idx ON public.orders USING btree (status, shipping_city);",
        ),
        # 155 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.orders_status_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_status_idx ON public.orders USING btree (status);",
        ),

        # =====================================================================
        # order_item_events indexes (non-Django table)
        # =====================================================================
        # 62.8 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.order_item_events_updated_at_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_item_events_updated_at_idx ON public.order_item_events USING btree (updated_at);",
        ),
        # 25.6 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.order_item_events_order_id_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_item_events_order_id_idx ON public.order_item_events USING btree (order_id);",
        ),
        # 17.4 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.order_item_events_customer_id_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_item_events_customer_id_idx ON public.order_item_events USING btree (customer_id);",
        ),

        # =====================================================================
        # payments indexes (non-Django table)
        # =====================================================================
        # 15.5 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.payments_provider_status_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY payments_provider_status_idx ON public.payments USING btree (provider, status);",
        ),
        # 15.5 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.payments_status_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY payments_status_idx ON public.payments USING btree (status);",
        ),
        # 15.4 MiB
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS public.payments_provider_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY payments_provider_idx ON public.payments USING btree (provider);",
        ),
    ]

