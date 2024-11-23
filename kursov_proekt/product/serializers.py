import serializer as serializer
from rest_framework import serializers

from kursov_proekt.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
