# Generated by Django 5.1.3 on 2024-12-12 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_alter_orderitems_size'),
        ('product', '0010_remove_product_max_price_accessory'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='accessory',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_items_accessory', to='product.accessory'),
        ),
    ]