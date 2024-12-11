from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Sum

from kursov_proekt.accounts.models import Profile
from kursov_proekt.product.choices import ColorChoice, BrandChoice, SizeChoiceShoes, SizeChoiceClothes


# Create your models here.


class Category(models.Model):
    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
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

    sku = models.CharField(
        max_length=100,
        unique=True
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
    num_of_times_purchased = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        permissions = [
            ('can_create_products', 'Can create products')
        ]

    def get_discounted_price(self):
        # Конвертирайте в Decimal
        return Decimal(self.discount_price) if self.discount_price else Decimal(self.price)

    def get_max_stock_quantity(self):
        # Използваме Sum за да вземем общото количество на всички размери
        total_quantity = self.sizes.aggregate(Sum('stock_quantity'))['stock_quantity__sum']
        return total_quantity if total_quantity else 0




class ProductSize(models.Model):
    SIZE_CHOICES_CLOTHES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    SIZE_CHOICES_SHOES = [
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
    ]

    SIZE_CHOICES = {
        'clothing': SIZE_CHOICES_CLOTHES,
        'shoes': SIZE_CHOICES_SHOES,
        'accessories': [],
    }

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10)
    max_size = models.PositiveIntegerField(null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - {self.size}"

    def clean(self):
        """Validate size according to product category and validate stock_quantity."""
        category_name = self.product.category.name.lower()  # Използваме по-малък регистър за по-добра съвместимост

        # Валидация на размера според категорията на продукта
        if category_name == 'shoes' and self.size not in dict(self.SIZE_CHOICES['shoes']):
            raise ValidationError(f"Invalid size for shoes: {self.size}.")
        elif category_name == 'clothing' and self.size not in dict(self.SIZE_CHOICES['clothing']):
            raise ValidationError(f"Invalid size for clothing: {self.size}.")
        elif category_name == 'accessories' and self.size is not None:
            raise ValidationError("Accessories should not have sizes.")

        # Валидация на количеството - не трябва да е отрицателно
        if self.stock_quantity < 0:
            raise ValidationError(f"Stock quantity cannot be negative. Provided value: {self.stock_quantity}.")

    def save(self, *args, **kwargs):
        """Override save method to validate before saving the instance."""
        """Override save method to validate before saving the instance."""
        self.clean()  # Call the validation logic before saving
        if not self.max_size:  # Ensure max_size is set if not already set
            self.max_size = self.stock_quantity
        super().save(*args, **kwargs)
        # Записваме модела, ако всички проверки преминат успешно

