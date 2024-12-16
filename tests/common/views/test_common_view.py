import shutil

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from kursov_proekt.product.models import Product, Category
from django.utils import timezone

from kursov_proekt.settings import MEDIA_ROOT


class HomePageTest(TestCase):

    def setUp(self):
        # Create a category to associate with the product
        self.category = Category.objects.create(name="Category 1")

        # Create a user without permission (assuming you are also testing user permissions)
        self.user_without_perm = get_user_model().objects.create_user(
            username='user_without_perm',
            email='user_without_perm@example.com',  # Provide a valid email
            password='password123'
        )

        # Create a user with permission
        self.user_with_perm = get_user_model().objects.create_user(
            username='user_with_perm',
            email='user_with_perm@example.com',  # Provide a valid email
            password='password123'
        )

        # Create a product and associate it with the category
        self.product = Product.objects.create(
            name="Product 1",
            price=100,
            num_of_times_purchased=6,
            created_at=timezone.now(),
            category=self.category  # Associate with the category
        )

    def test_home_page_with_permissions(self):
        # Set up temporary file storage
        fs = FileSystemStorage(location='/tmp')  # or a suitable temporary directory

        # Create an image file in memory for testing
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        # Create a category for the product
        category = Category.objects.create(name="Test Category")

        # Ensure sku is provided and unique
        sku_value = "SKU12345"

        # Create the Product with the main_image field set to the uploaded image
        instance = Product.objects.create(
            name="Product with Image",
            price=50,
            num_of_times_purchased=10,
            created_at=timezone.now(),
            category=category,
            main_image=image,
            sku=sku_value
        )

        # Make a GET request to the home page with permissions
        self.client.login(username='user_with_perm', password='password123')
        response = self.client.get(reverse('common'))

        # Check the response status and other assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'common/index.html')
        self.assertTrue(response.context['has_perm'])

        # Check that 'best_sellers' and 'new_arrivals' have correct data
        best_sellers = response.context['best_sellers']
        self.assertEqual(len(best_sellers), 3)
        self.assertTrue(all(product.num_of_times_purchased > 5 for product in best_sellers))

        new_arrivals = response.context['new_arrivals']
        self.assertEqual(len(new_arrivals), 3)
        self.assertTrue(all(product.created_at >= new_arrivals[-1].created_at for product in new_arrivals))

    def tearDown(self):
        shutil.rmtree(MEDIA_ROOT)

    def test_home_page_without_permissions(self):
        # Log in the user without permissions
        self.client.login(username='user_without_perm', password='password123')

        # Request the home page
        response = self.client.get(reverse('common'))

        # Check that the response status is OK (200)
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'common/index.html')

        # Check the 'has_perm' context variable (should be False)
        self.assertFalse(response.context['has_perm'])

        # Check the 'best_sellers' context variable (should contain 3 products with num_of_times_purchased > 5)
        best_sellers = response.context['best_sellers']
        self.assertEqual(len(best_sellers), 3)
        self.assertTrue(all(product.num_of_times_purchased > 5 for product in best_sellers))

        # Check the 'new_arrivals' context variable (should contain the most recent 3 products)
        new_arrivals = response.context['new_arrivals']
        self.assertEqual(len(new_arrivals), 3)
        self.assertTrue(all(product.created_at >= new_arrivals[-1].created_at for product in new_arrivals))
