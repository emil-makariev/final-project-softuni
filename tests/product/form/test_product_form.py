from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.core.exceptions import ValidationError
from kursov_proekt.product.models import Product, Category, ProductSize, Accessory
from kursov_proekt.product.forms import BaseProduct
from django.db import IntegrityError


class ProductFormTests(TestCase):

    def setUp(self):
        # Create some categories for testing
        self.category_clothing = Category.objects.create(name='Clothing')
        self.category_accessories = Category.objects.create(name='Accessories')
        self.category_shoes = Category.objects.create(name='Shoes')



    def test_product_form_valid_data_clothing(self):
            # Prepare form data
            data = {
                'name': 'T-Shirt',
                'description': 'A cool t-shirt',
                'price': 25.0,
                'discount_price': 20.0,
                'color': 'red',  # Ensure this is valid in ColorChoice
                'sku': 12345,
                'category': self.category_clothing,  # Pass the full Category object, not just the ID
                'brand': 'Hermes',  # Ensure this is valid in BrandChoice
                'xs_quantity': 10,
                's_quantity': 20,
                'm_quantity': 30,
                'l_quantity': 40,
                'xl_quantity': 50,
            }

            # Prepare the file (mock file for testing)
            file = SimpleUploadedFile("image.jpg", b"file_content_here", content_type="image/jpeg")

            # Create the form with data and file
            form = BaseProduct(data=data, files={'main_image': file})

            # Check if the form is valid
            print("Form Errors:", form.errors)  # Debug form errors
            self.assertTrue(form.is_valid())

            # Save the product if the form is valid
            product = form.save()

            # Check if the product and product sizes are saved correctly
            self.assertEqual(Product.objects.count(), 1)
            self.assertEqual(ProductSize.objects.count(), 5)  # We expect sizes XS, S, M, L, XL to be created
            self.assertEqual(product.name, 'T-Shirt')

    def test_product_form_valid_data_accessory(self):
        # Prepare form data (without the file)
        data = {
            'name': 'Belt',
            'description': 'A stylish belt',
            'price': 15.0,
            'discount_price': 10.0,
            'color': 'black',  # Ensure this matches valid ColorChoice
            'sku': 67890,
            'category': self.category_accessories,
            'brand': 'Hermes',  # Ensure this is a valid choice in BrandChoice
            'accessory_quantity': 100,
        }

        # Prepare the file (as a mock uploaded file)
        file = SimpleUploadedFile("belt_image.jpg", b"file_content_here", content_type="image/jpeg")

        # Create the form with data and file
        form = BaseProduct(data=data, files={'main_image': file})

        # Check if form is valid
        self.assertTrue(form.is_valid())

        # Save the product if form is valid
        product = form.save()

        # Check product count and attributes
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Accessory.objects.count(), 1)
        self.assertEqual(product.name, 'Belt')

    def test_product_form_invalid_data(self):
        # Test with missing required fields or invalid data
        data = {
            'name': 'Invalid Product',
            'description': 'Invalid product description',
            'price': -5.0,  # Invalid price (negative value)
            'discount_price': -2.0,  # Invalid price (negative value)
            'color': 'Blue',
            'main_image': 'invalid_image.jpg',
            'sku': 12345,
            'category': self.category_clothing.id,
            'brand': 'Brand C',
            'xs_quantity': 0,
            's_quantity': 0,
            'm_quantity': 0,
            'l_quantity': 0,
            'xl_quantity': 0,
        }

        form = BaseProduct(data=data)

        self.assertFalse(form.is_valid())  # Form should be invalid due to negative price

        # Check if validation errors are present
        self.assertIn('price', form.errors)
        self.assertIn('discount_price', form.errors)

    def test_product_form_edge_case_non_integer_quantity(self):
        # Test with non-integer value for quantity
        data = {
            'name': 'Sweater',
            'description': 'A cozy sweater',
            'price': 40.0,
            'discount_price': 35.0,
            'color': 'Green',
            'main_image': 'sweater_image.jpg',
            'sku': 67890,
            'category': self.category_clothing.id,
            'brand': 'Brand D',
            'xs_quantity': 'ten',  # Non-integer value
            's_quantity': 20,
            'm_quantity': 30,
            'l_quantity': 40,
            'xl_quantity': 50,
        }

        form = BaseProduct(data=data)

        self.assertFalse(form.is_valid())  # Form should be invalid due to non-integer quantity
        self.assertIn('xs_quantity', form.errors)  # Check if the error is specifically for xs_quantity

    def test_product_form_zero_quantity(self):
        # Prepare data with zero quantity for all sizes
        data = {
            'name': 'T-Shirt',
            'description': 'A cool t-shirt',
            'price': 25.0,
            'discount_price': 20.0,
            'color': 'red',  # Ensure this is valid in ColorChoice
            'sku': 12345,
            'category': self.category_clothing,  # Pass the full Category object, not just the ID
            'brand': 'Hermes',  # Ensure this is valid in BrandChoice
            'xs_quantity': 0,  # Test zero quantity
            's_quantity': 0,
            'm_quantity': 0,
            'l_quantity': 0,
            'xl_quantity': 0,
        }

        # Prepare the file (mock file for testing)
        file = SimpleUploadedFile("image.jpg", b"file_content_here", content_type="image/jpeg")

        # Create the form with data and file
        form = BaseProduct(data=data, files={'main_image': file})

        # Print the errors to see why the form is invalid
        print("Form Errors:", form.errors)

        # Check if the form is valid
        self.assertTrue(form.is_valid(), "Form is invalid due to the following errors: " + str(form.errors))

        # Save the product if the form is valid
        product = form.save()

        # Check if the product is saved correctly
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(ProductSize.objects.count(), 5)  # We expect sizes XS, S, M, L, XL to be created
        self.assertEqual(product.name, 'T-Shirt')

