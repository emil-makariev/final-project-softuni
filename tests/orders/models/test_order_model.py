from django.test import TestCase
from django.utils import timezone
from kursov_proekt.accounts.models import Profile, CustomBaseUser
from kursov_proekt.product.models import Product, ProductSize, Accessory, Category
from kursov_proekt.orders.models import Orders, OrderItems, BillingDetails

class OrderModelTest(TestCase):

    def setUp(self):
        # Step 1: Create the CustomBaseUser instance
        self.user = CustomBaseUser.objects.create_user(
            username="testuser",
            password="password123",
            email="testuser@example.com"
        )

        # Step 2: Ensure no Profile exists for the user
        Profile.objects.filter(user=self.user).delete()  # Delete any existing profiles for this user

        # Step 3: Create the Profile instance, linking it to the CustomBaseUser
        self.profile = Profile.objects.create(
            user=self.user,  # Link the profile to the created user
            shipping_address_line1="123 Main St",
            shipping_address_line2="Apt 4",
            city="Cityville",
            state="State",
            postal_code="12345",
            country="Country",
        )

        # Step 4: Create Category instance
        self.category = Category.objects.create(name="Sample Category")

        # Step 5: Create a Product instance and assign category
        self.product = Product.objects.create(
            name="Sample Product",
            price=100.00,
            category=self.category  # Assign the category to the product
        )

        # Step 6: Create ProductSize instance and assign the product
        self.size = ProductSize.objects.create(
            size="M",
            product=self.product  # Ensure a product is assigned
        )

        # Step 7: Create an Accessory instance, linking it to the product
        self.accessory = Accessory.objects.create(
            product=self.product,  # Link the accessory to the created product
            stock_quantity=10  # Set the stock quantity (default is 10, so this is optional)
        )

        # Step 8: Create an Order linked to the profile
        self.order = Orders.objects.create(
            profile=self.profile,  # Link the order to the created profile
            total_price=200.00,
            discount_codes="DISCOUNT20",
            discount_amount=20.00,
            status=True
        )

        # Step 9: Create OrderItems instances linked to the order
        self.order_item1 = OrderItems.objects.create(
            order=self.order,
            product=self.product,
            size=self.size
        )

        self.order_item2 = OrderItems.objects.create(
            order=self.order,
            product=self.product,
            accessory=self.accessory
        )

        # Step 10: Create BillingDetails instance linked to the order
        self.billing_details = BillingDetails.objects.create(
            order=self.order,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="123-456-7890",
            address="123 Main St",
            city="Cityville",
            postal_code="12345",
            country="Country",
            account_password="password123",
            order_notes="Leave at the door."
        )

    def test_order_creation(self):
        """Test the creation of an order."""
        self.assertEqual(self.order.total_price, 200.00)
        self.assertEqual(self.order.discount_codes, "DISCOUNT20")
        self.assertEqual(self.order.status, True)
        self.assertEqual(self.order.profile, self.profile)
        self.assertIsInstance(self.order.created_at, timezone.datetime)
        self.assertIsInstance(self.order.updated_at, timezone.datetime)

    def test_order_item_creation(self):
        """Test the creation of order items."""
        self.assertEqual(self.order_item1.product, self.product)
        self.assertEqual(self.order_item1.size, self.size)
        self.assertEqual(self.order_item2.product, self.product)
        self.assertEqual(self.order_item2.accessory, self.accessory)
        self.assertEqual(self.order_item1.order, self.order)
        self.assertEqual(self.order_item2.order, self.order)

    def test_billing_details_creation(self):
        """Test the creation of billing details."""
        self.assertEqual(self.billing_details.first_name, "John")
        self.assertEqual(self.billing_details.last_name, "Doe")
        self.assertEqual(self.billing_details.email, "john.doe@example.com")
        self.assertEqual(self.billing_details.phone_number, "123-456-7890")
        self.assertEqual(self.billing_details.address, "123 Main St")
        self.assertEqual(self.billing_details.city, "Cityville")
        self.assertEqual(self.billing_details.postal_code, "12345")
        self.assertEqual(self.billing_details.country, "Country")
        self.assertEqual(self.billing_details.order_notes, "Leave at the door.")
        self.assertEqual(self.billing_details.order, self.order)

    def test_order_billing_details_relationship(self):
        """Test the relationship between Orders and BillingDetails."""
        self.assertEqual(self.billing_details.order, self.order)
        self.assertEqual(self.order.billing_details.first_name, "John")

    def test_order_item_product_relationship(self):
        """Test the relationship between OrderItems and Product."""
        self.assertEqual(self.order_item1.product.name, "Sample Product")
        self.assertEqual(self.order_item2.product.name, "Sample Product")

    def test_order_item_size_relationship(self):
        """Test the relationship between OrderItems and ProductSize."""
        self.assertEqual(self.order_item1.size.size, "M")

    def test_order_item_accessory_relationship(self):
        # Make sure the accessory is correctly linked to the product
        self.assertEqual(self.order_item2.accessory.product.name, "Sample Product")
        self.assertEqual(self.order_item2.accessory.stock_quantity, 10)  # Check stock quantity as an example

    def test_order_status_update(self):
        """Test the status update of an order."""
        self.order.status = False
        self.order.save()
        self.assertEqual(self.order.status, False)

    def test_order_total_price_calculation(self):
        """Test the total price calculation for orders."""
        self.assertEqual(self.order.total_price, 200.00)

    def test_order_with_discount(self):
        """Test that the order reflects the discount correctly."""
        expected_total_price = self.order.total_price - self.order.discount_amount
        self.assertEqual(self.order.total_price, 200.00)
        self.assertEqual(self.order.discount_amount, 20.00)
        self.assertEqual(self.order.total_price - self.order.discount_amount, expected_total_price)

