# Generated migration to drop unused indexes
# Issue: https://console.postgres.ai/goodvibes-ai/issues/019b3336-fb12-7072-b792-3233ffbcd699
#
# This migration drops 31 unused indexes consuming 19.2 GiB as identified by
# postgres.ai index analysis over 36 days of statistics.
#
# IMPORTANT NOTES:
# - All DROP INDEX operations use CONCURRENTLY to avoid blocking writes
# - This migration is non-atomic (atomic = False) because DROP INDEX CONCURRENTLY
#   cannot run inside a transaction block
# - The reverse migration recreates indexes with CONCURRENTLY as well
# - If you need to test the impact before dropping, consider using HypoPG:
#   SELECT hypopg_hide_index('schema.index_name'); to simulate removal
# - Alternative soft-drop: UPDATE pg_index SET indisvalid = false WHERE indexrelid = 'idx_name'::regclass;
#   (requires superuser, index still maintained but ignored by planner)

from django.db import migrations
from django.contrib.postgres.operations import RemoveIndexConcurrently


class Migration(migrations.Migration):
    # CONCURRENTLY operations cannot run in a transaction
    atomic = False

    dependencies = [
        ("shop", "0003_remove_orderitem_idx_orderitem_order_only_2"),
    ]

    operations = [
        # ============================================================
        # Product indexes (4 explicit + 1 auto-generated _like index)
        # ============================================================
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_sku_nonunique",
        ),
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_is_active",
        ),
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_name_plain",
        ),
        RemoveIndexConcurrently(
            model_name="product",
            name="idx_product_name_lower",
        ),
        # Django auto-generated _like index for varchar pattern ops
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS shop_product_sku_20049d15_like;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_product_sku_20049d15_like ON shop_product (sku varchar_pattern_ops);",
        ),
        # ============================================================
        # Customer indexes (2 explicit + 1 auto-generated _like index)
        # ============================================================
        RemoveIndexConcurrently(
            model_name="customer",
            name="idx_customer_email_plain",
        ),
        RemoveIndexConcurrently(
            model_name="customer",
            name="idx_customer_email_lower",
        ),
        # Django auto-generated _like index for varchar pattern ops
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS shop_customer_email_d3fdf104_like;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_customer_email_d3fdf104_like ON shop_customer (email varchar_pattern_ops);",
        ),
        # ============================================================
        # Order indexes (5 explicit + 1 auto-generated FK index)
        # ============================================================
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_customer_created_at",
        ),
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_customer_only",
        ),
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_cancelled_full",
        ),
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_cust_inc_created",
        ),
        RemoveIndexConcurrently(
            model_name="order",
            name="idx_order_cancelled_partial",
        ),
        # Django auto-generated FK index
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS shop_order_customer_id_f638df20;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_order_customer_id_f638df20 ON shop_order (customer_id);",
        ),
        # ============================================================
        # OrderItem indexes (3 explicit + 2 auto-generated FK indexes)
        # ============================================================
        RemoveIndexConcurrently(
            model_name="orderitem",
            name="idx_orderitem_order_product",
        ),
        RemoveIndexConcurrently(
            model_name="orderitem",
            name="idx_oi_prod_order_bad",
        ),
        RemoveIndexConcurrently(
            model_name="orderitem",
            name="idx_orderitem_order_only",
        ),
        # Django auto-generated FK indexes
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS shop_orderitem_order_id_2f1b00cf;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_orderitem_order_id_2f1b00cf ON shop_orderitem (order_id);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS shop_orderitem_product_id_48153f22;",
            reverse_sql="CREATE INDEX CONCURRENTLY shop_orderitem_product_id_48153f22 ON shop_orderitem (product_id);",
        ),
        # ============================================================
        # Non-Django managed tables (raw SQL required)
        # These tables exist in the database but are not managed by Django models
        # ============================================================
        # orders table (4 indexes)
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS orders_customer_created_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_customer_created_idx ON orders (customer_id, created_at);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS orders_customer_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_customer_idx ON orders (customer_id);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS orders_status_city_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_status_city_idx ON orders (status, city);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS orders_status_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY orders_status_idx ON orders (status);",
        ),
        # order_items table (2 indexes)
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS order_items_order_sku_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_items_order_sku_idx ON order_items (order_id, sku);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS order_items_sku_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_items_sku_idx ON order_items (sku);",
        ),
        # order_item_events table (3 indexes)
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS order_item_events_updated_at_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_item_events_updated_at_idx ON order_item_events (updated_at);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS order_item_events_order_id_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_item_events_order_id_idx ON order_item_events (order_id);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS order_item_events_customer_id_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY order_item_events_customer_id_idx ON order_item_events (customer_id);",
        ),
        # payments table (3 indexes)
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS payments_provider_status_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY payments_provider_status_idx ON payments (provider, status);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS payments_status_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY payments_status_idx ON payments (status);",
        ),
        migrations.RunSQL(
            sql="DROP INDEX CONCURRENTLY IF EXISTS payments_provider_idx;",
            reverse_sql="CREATE INDEX CONCURRENTLY payments_provider_idx ON payments (provider);",
        ),
    ]

