from rest_framework import serializers
from .models import WishlistItem

class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ['id', 'wishlist', 'product']
