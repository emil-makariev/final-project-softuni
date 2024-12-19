from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from kursov_proekt.orders.models import Orders, OrderItems, BillingDetails
from kursov_proekt.product.models import Product, ProductSize, Category
from decimal import Decimal


class DashboardProductCartsTests(TestCase):
    def setUp(self):
        # Create a user using the custom user model
        User = get_user_model()  # This will use your CustomBaseUser model
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )
        # Ensure a profile is created for the user
        self.profile = self.user.profile

        # Create a category for the product
        self.category = Category.objects.create(name="Test Category")

        # Create a product and product size for the order item
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            category=self.category  # Assign category here
        )
        self.size = ProductSize.objects.create(product=self.product, size='M', stock_quantity=5, max_size=5)

        # Create an order linked to the user's profile
        self.order = Orders.objects.create(profile=self.profile, status=False)
        # Create an order item for the product and size
        self.order_item = OrderItems.objects.create(order=self.order, product=self.product, size=self.size)

        # Log in the user
        self.client.login(username='testuser', password='password')

    def test_dashboard_product_carts_view(self):
        url = reverse('all-products-carts', args=[self.profile.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'M')
        self.assertContains(response, '10')
        self.assertContains(response, '5')  # max size



class AddToOrderTests(TestCase):
    def setUp(self):
        # Create a user using the custom user model
        User = get_user_model()  # This will use your CustomBaseUser model
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )
        # Ensure a profile is created for the user
        self.profile = self.user.profile

        # Create a category (which is required for Product)
        self.category = Category.objects.create(name='Test Category')

        # Create a product and product size for the order item
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            category=self.category,  # Associate the category here
        )
        self.size = ProductSize.objects.create(
            product=self.product,
            size='M',
            stock_quantity=5,
            max_size=5
        )
        # Log in the user
        self.client.login(username='testuser', password='password')

    def test_add_to_order_valid(self):
        url = reverse('add_to_order')
        data = {'product_id': self.product.id, 'size_id': self.size.id, 'quantity': 1}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'success',
            'message': 'Item added to order',
            'order_item_id': 1  # Expecting the order_item_id to be part of the response
        })

    def test_add_to_order_invalid_product(self):
        url = reverse('add_to_order')
        data = {'product_id': 999, 'size_id': self.size.id, 'quantity': 1}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'detail': 'Product not found.'})

    def test_add_to_order_invalid_size(self):
        url = reverse('add_to_order')
        data = {'product_id': self.product.id, 'size_id': 999, 'quantity': 1}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'detail': 'Size not found.'})

class FinalizeOrderTests(TestCase):
    def setUp(self):
        # Create a user and login
        self.user = get_user_model().objects.create_user(
            username='testuser', email='testuser@example.com', password='password'
        )
        self.client.login(username='testuser', password='password')

        # Create a category
        self.category = Category.objects.create(name="Test Category")

        # Create product and product size
        self.product = Product.objects.create(name="Test Product", price=Decimal('10.00'), category=self.category)
        self.size = ProductSize.objects.create(product=self.product, size='M', stock_quantity=5, max_size=5)

        # Create an order linked to the user
        self.order = Orders.objects.create(profile=self.user.profile, status=False)

        # Add order item
        self.order_item = OrderItems.objects.create(order=self.order, product=self.product, size=self.size)

    def test_finalize_order_get(self):
        url = reverse('check_out', args=[self.user.profile.pk])  # Update with your URL name
        response = self.client.get(url)

        # Ensure the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Checkout')  # Ensure the page contains the word "Checkout"
        self.assertIn('form', response.context)  # Ensure the form is passed in context
        self.assertIn('order', response.context)  # Ensure the order is passed in context
        self.assertIn('grouped_items', response.context)  # Ensure grouped items are passed in context

    def test_finalize_order_post_valid(self):
        # Ensure the user is logged in
        self.client.login(username='testuser', password='password')

        url = reverse('check_out', args=[self.user.profile.pk])  # Update with your URL name
        data = {
            'address': '123 Main St',
            'payment_method': 'Credit Card',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'city': 'New York',
            'postal_code': '10001',
            'country': 'USA',
            'account_password': 'password123',
            'order_notes': 'Please deliver between 2-4 PM.'
        }

        # Send the POST request and follow the redirect
        response = self.client.post(url, data, follow=True)

        # Ensure we are redirected to the correct page
        self.assertEqual(response.status_code, 200)

        # Check if the order status was updated
        self.order.refresh_from_db()
        self.assertTrue(self.order.status, "Order status was not updated correctly.")

        # Define the success_url for your test (same as in your view)
        success_url = reverse('after_purchesing')

        # Check the final destination URL after redirect
        self.assertRedirects(response, success_url)

        # Verify if the stock quantity has been updated
        self.size.refresh_from_db()  # Make sure to refresh the instance to get the updated stock quantity
        self.assertEqual(self.size.stock_quantity, 5)

    def test_finalize_order_post_invalid(self):
        url = reverse('check_out', args=[self.user.profile.pk])  # Update with your URL name
        data = {
            'address': '',  # Missing address
            'payment_method': 'Credit Card'
        }

        response = self.client.post(url, data)

        # Ensure the form is not valid
        self.assertFormError(response, 'form', 'address', 'This field is required.')

        # Ensure the order status is not changed (remains False)
        self.order.refresh_from_db()
        self.assertFalse(self.order.status)


    def test_finalize_order_for_non_existing_order(self):
        # Try accessing a non-existing order
        url = reverse('check_out', args=[9999])  # Use a non-existent user profile pk
        response = self.client.get(url)

        # Ensure a 404 error is raised
        self.assertEqual(response.status_code, 404)



class OrderListViewTests(TestCase):
    def setUp(self):
        # Create a user using the custom user model
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )

        # Ensure a profile is created for the user
        self.profile = self.user.profile

        # Create a category for the product (this is necessary to satisfy the NOT NULL constraint)
        self.category = Category.objects.create(name='Test Category')

        # Create a product with a category and product size for the order item
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            category=self.category  # Assign the category
        )

        # Create a product size for the product
        self.size = ProductSize.objects.create(
            product=self.product,
            size='M',
            stock_quantity=5,
            max_size=5
        )

        # Create an order linked to the user's profile
        self.order = Orders.objects.create(profile=self.profile, status=False)

        # Create an order item for the product and size
        self.order_item = OrderItems.objects.create(order=self.order, product=self.product, size=self.size)

        # Log in the user
        self.client.login(username='testuser', password='password')

    def test_order_list_view(self):
        url = reverse('check_out', args=[self.profile.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'M')

# Other tests can be similarly updated to ensure they use the custom user model (CustomBaseUser)
