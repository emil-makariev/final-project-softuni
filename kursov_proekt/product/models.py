from django.db import models

from kursov_proekt.product.choices import SizeChoice, ColorChoice, BrandChoice


# Create your models here.


class Category(models.Model):
    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(
        max_length=255
    )
    description = models.TextField(

    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True)
    stock_quantity = models.IntegerField(
        default=0
    )
    sku = models.CharField(
        max_length=100,
        unique=True
    )
    size = models.CharField(
        choices=SizeChoice
    )
    color = models.CharField(
        choices = ColorChoice
    )

    main_image = models.ImageField(
        upload_to='mediafiles/'
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
    )

    brand = models.CharField(
        choices=BrandChoice
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        permissions = [
            ('can_create_products', 'Can create products')
        ]

    def get_discounted_price(self):
        return self.discount_price if self.discount_price else self.price

    def in_stock(self):
        return self.stock_quantity > 0

