# Generated manually to address H002 Unused Indexes issue
# Issue: https://console.postgres.ai/goodvibes-ai/issues/019a5a58-582f-7819-9377-b40d207aa220
# Drops 9 unused indexes consuming 3.36 GiB of storage

from django.db import migrations
from django.contrib.postgres.operations import RemoveIndexConcurrently


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('shop', '0003_remove_orderitem_idx_orderitem_order_only_2'),
    ]

    operations = [
        # Drop unused indexes from Product table (4 indexes, ~2.26 GiB)
        RemoveIndexConcurrently(
            model_name='product',
            name='idx_product_sku_nonunique',
        ),
        RemoveIndexConcurrently(
            model_name='product',
            name='idx_product_is_active',
        ),
        RemoveIndexConcurrently(
            model_name='product',
            name='idx_product_name_plain',
        ),
        RemoveIndexConcurrently(
            model_name='product',
            name='idx_product_name_lower',
        ),
        
        # Drop unused index from Customer table (1 index, 206 MiB)
        RemoveIndexConcurrently(
            model_name='customer',
            name='idx_customer_email_plain',
        ),
        
        # Drop unused indexes from Order table (3 indexes, ~397 MiB)
        RemoveIndexConcurrently(
            model_name='order',
            name='idx_order_customer_only',
        ),
        RemoveIndexConcurrently(
            model_name='order',
            name='idx_order_cust_inc_created',
        ),
        RemoveIndexConcurrently(
            model_name='order',
            name='idx_order_cancelled_full',
        ),
        
        # Drop unused index from OrderItem table (1 index, 132 MiB)
        RemoveIndexConcurrently(
            model_name='orderitem',
            name='idx_oi_prod_order_bad',
        ),
    ]

