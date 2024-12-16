import time

from django.test import TestCase
from django.core.exceptions import ValidationError
from kursov_proekt.product.models import Product, Category, ProductSize
from decimal import Decimal


class ProductModelTest(TestCase):

    def setUp(self):
        # Create a category for the product
        self.category = Category.objects.create(name="Clothing")

    def test_price_validation(self):
        # Create a category for the product
        self.category = Category.objects.create(name="Clothing")

        # Create a product with an invalid price (below minimum)
        invalid_product = Product.objects.create(
            name=f"Invalid Product {int(time.time())}",
            description="A product with an invalid price",
            price=0.5,  # Invalid price (below minimum)
            sku="654321",
            color="Blue",
            main_image="dummy_image.jpg",
            category=self.category,
            brand="Brand B"
        )

        # Explicitly call full_clean to trigger validation
        with self.assertRaises(ValidationError):
            invalid_product.full_clean()  # This will trigger validation

    def test_discount_price(self):
        # Product without discount price
        product_no_discount = Product.objects.create(
            name="Product No Discount",
            description="Product without a discount price",
            price=100.0,
            sku="123457",
            color="Black",
            main_image="dummy_image.jpg",
            category=self.category,
            brand="Brand D"
        )
        # The discounted price should be the same as the original price
        self.assertEqual(product_no_discount.get_discounted_price(), Decimal("100.00"))

        # Product with discount price
        product_with_discount = Product.objects.create(
            name="Product With Discount",
            description="Product with a discount price",
            price=100.0,
            discount_price=80.0,  # Discounted price
            sku="123458",
            color="White",
            main_image="dummy_image.jpg",
            category=self.category,
            brand="Brand E"
        )
        # The discounted price should be 80.00
        self.assertEqual(product_with_discount.get_discounted_price(), Decimal("80.00"))

    def test_discount_price_default(self):
        # Product without providing a discount price
        product = Product.objects.create(
            name="Product Default Discount",
            description="Product with default discount price",
            price=100.0,
            sku="123459",
            color="Yellow",
            main_image="dummy_image.jpg",
            category=self.category,
            brand="Brand F"
        )
        # Ensure that the default discount price is 0.00
        self.assertEqual(product.discount_price, 0.00)

    def test_invalid_size_for_product(self):
        # Create a product with a category for clothing
        category = Category.objects.create(name="Clothing")
        product = Product.objects.create(
            name="Clothing Product",
            description="Product with invalid size",
            price=50.0,
            sku="123460",
            color="Pink",
            main_image="dummy_image.jpg",
            category=category,
            brand="Brand G"
        )

        # Try creating a ProductSize with an invalid size (should raise validation error)
        invalid_size = ProductSize(
            product=product,
            size="XXL",  # Invalid size for clothing
            stock_quantity=10
        )

        with self.assertRaises(ValidationError):
            invalid_size.full_clean()  # This triggers the validation logic

    def test_valid_size_for_product(self):
        category = Category.objects.create(name="Clothing")
        product = Product.objects.create(
            name="Clothing Product",
            description="Product with valid size",
            price=50.0,
            sku="123461",
            color="Blue",
            main_image="dummy_image.jpg",
            category=category,
            brand="Brand H"
        )

        # Try creating a ProductSize with a valid size (should not raise error)
        valid_size = ProductSize(
            product=product,
            size="M",  # Valid size
            stock_quantity=10
        )
        try:
            valid_size.full_clean()  # This should pass without errors
        except ValidationError:
            self.fail("ProductSize with valid size raised ValidationError unexpectedly!")

    def test_stock_quantity_validation(self):
        category = Category.objects.create(name="Clothing")
        product = Product.objects.create(
            name="Clothing Product",
            description="Product with negative stock quantity",
            price=50.0,
            sku="123462",
            color="Purple",
            main_image="dummy_image.jpg",
            category=category,
            brand="Brand I"
        )

        # Try creating a ProductSize with a negative stock_quantity (should raise validation error)
        invalid_stock_quantity = ProductSize(
            product=product,
            size="L",
            stock_quantity=-5  # Invalid stock quantity
        )
        with self.assertRaises(ValidationError):
            invalid_stock_quantity.full_clean()  # This triggers the validation logic
