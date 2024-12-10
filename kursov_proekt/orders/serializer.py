import serializer as serializer
from rest_framework import serializers
from decimal import Decimal

from kursov_proekt.accounts.models import Profile
from kursov_proekt.orders.models import OrderItems, Orders
from kursov_proekt.product.models import Product, ProductSize


class OrderItemsSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    size = serializers.PrimaryKeyRelatedField(queryset=ProductSize.objects.all())  # Reference to ProductSize model

    class Meta:
        model = OrderItems
        fields = ['product', 'size']

    def create(self, validated_data):
        user = self.context['request'].user  # Get the logged-in user

        profile = user.profile  # Assuming each user has a profile
        order, created = Orders.objects.get_or_create(
            profile=profile,
            status=False  # Assuming False means 'pending' order status
        )

        product = validated_data['product']
        size = validated_data['size']  # Get the size from validated data

        # Calculate the price for this item based on the quantity
        price = Decimal(product.price)

        # Create the order item
        order_item = OrderItems.objects.create(
            order=order,
            product=product,
            size=size  # Store the size (ProductSize instance) in OrderItems
        )

        # Update the total price of the order
        order.total_price += price
        order.save()

        return order_item



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'
