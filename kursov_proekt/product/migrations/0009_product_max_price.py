# Generated by Django 5.1.3 on 2024-12-11 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_product_num_of_times_purchased'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
