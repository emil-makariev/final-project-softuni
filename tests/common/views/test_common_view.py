from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model  # Use this to get the custom user model
from django.contrib.contenttypes.models import ContentType
from kursov_proekt.product.models import Product, Category
from django.contrib.auth.models import Permission, Group


class HomePageViewTest(TestCase):
    def setUp(self):
        # Use the custom user model instead of the default User model
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create the permission and group for the user
        self.product_permission = Permission.objects.get(codename='can_create_products')
        self.group = Group.objects.create(name='Product Managers')
        self.group.permissions.add(self.product_permission)
        self.user.groups.add(self.group)
        self.user.save()

        # Create categories
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Clothing')

        # Create test products with all required fields, including category, price, and unique SKU
        self.product1 = Product.objects.create(name='Best Seller 1', num_of_times_purchased=10, created_at='2023-01-01',
                                               price=100, category=self.category1, sku='SKU001')
        self.product2 = Product.objects.create(name='Best Seller 2', num_of_times_purchased=15, created_at='2023-02-01',
                                               price=150, category=self.category1, sku='SKU002')
        self.product3 = Product.objects.create(name='Best Seller 3', num_of_times_purchased=20, created_at='2023-03-01',
                                               price=200, category=self.category2, sku='SKU003')
        self.product4 = Product.objects.create(name='New Arrival 1', num_of_times_purchased=1, created_at='2023-12-01',
                                               price=50, category=self.category2, sku='SKU004')
        self.product5 = Product.objects.create(name='New Arrival 2', num_of_times_purchased=1, created_at='2023-12-10',
                                               price=75, category=self.category1, sku='SKU005')
        self.product6 = Product.objects.create(name='New Arrival 3', num_of_times_purchased=1, created_at='2023-12-15',
                                               price=80, category=self.category1, sku='SKU006')

        # Log in the user
        self.client.login(username='testuser', password='password123')

    def test_homepage_status_code(self):
        # Check that the page returns a 200 status code
        response = self.client.get(reverse('common'))
        self.assertEqual(response.status_code, 200)

    def test_context_data_best_sellers(self):
        # Check that the context contains 'best_sellers' with the correct products
        response = self.client.get(reverse('common'))
        best_sellers = response.context['best_sellers']
        self.assertEqual(len(best_sellers), 3)
        self.assertEqual(best_sellers[0], self.product3)  # The product with the highest purchases
        self.assertEqual(best_sellers[1], self.product2)
        self.assertEqual(best_sellers[2], self.product1)

    def test_context_data_new_arrivals(self):
        # Check that the context contains 'new_arrivals' with the correct products
        response = self.client.get(reverse('common'))
        new_arrivals = response.context['new_arrivals']
        self.assertEqual(len(new_arrivals), 3)
        self.assertEqual(new_arrivals[0], self.product6)  # The most recent product
        self.assertEqual(new_arrivals[1], self.product5)
        self.assertEqual(new_arrivals[2], self.product4)

    def test_user_permission_in_context(self):
        # Check if the user has the correct permission in the context
        response = self.client.get(reverse('common'))
        self.assertTrue(response.context['has_perm'])

    def test_user_without_permission(self):
        # Test for a user without the 'product.can_create_products' permission
        user_without_permission = get_user_model().objects.create_user(
            username='user_without_permission',
            email='user_without_permission@example.com',  # Provide a unique email
            password='password123'
        )
        self.client.login(username='user_without_permission', password='password123')
        response = self.client.get(reverse('common'))
        self.assertFalse(response.context['has_perm'])
