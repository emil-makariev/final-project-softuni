from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from kursov_proekt.accounts.models import Profile
from kursov_proekt.product.models import Product, ProductSize, Accessory


# Create your models here.
class Orders(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    total_price = models.FloatField(
        validators=
        [MinValueValidator(0.00), MaxValueValidator(1000.00)],
        default=0.00

    )

    discount_codes = models.CharField(
        max_length=50, blank=True, null=True,
    )
    discount_amount = models.FloatField(
        validators=
        [MinValueValidator(1.00), MaxValueValidator(1000.00)],
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

    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='order_items', default=None,  null=True, blank=True)
    accessory = models.ForeignKey(Accessory,  on_delete=models.CASCADE, related_name='order_items_accessory', default=None,  null=True, blank=True)

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
    email = models.EmailField(
    )
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
    order_notes = models.CharField(
        max_length=500,
    )

    def __str__(self):
        return f"Billing details for Order {self.order.id}"