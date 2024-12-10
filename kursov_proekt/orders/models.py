from django.db import models

from kursov_proekt.accounts.models import Profile
from kursov_proekt.product.models import Product, ProductSize


# Create your models here.
class Orders(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )

    discount_codes = models.CharField(
        max_length=50, blank=True, null=True,
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
    )

    status = models.BooleanField(
        default=False
    )

    profile = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        related_name='order'
    )


class OrderItems(models.Model):

    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='order_items', default=None)

    order = models.ForeignKey(
        to=Orders,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='items'
    )


class BillingDetails(models.Model):
    order = models.OneToOneField(
        Orders,
        on_delete=models.CASCADE,
        related_name='billing_details',
        primary_key = True,
    )
    first_name = models.CharField(
        max_length=100
    )
    last_name = models.CharField(
        max_length=100
    )
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=20
    )
    address = models.CharField(
        max_length=255
    )
    city = models.CharField(
        max_length=100
    )
    postal_code = models.CharField(
        max_length=20
    )
    country = models.CharField(
        max_length=100
    )
    age = models.IntegerField(

    )

    def __str__(self):
        return f"Billing details for Order {self.order.id}"