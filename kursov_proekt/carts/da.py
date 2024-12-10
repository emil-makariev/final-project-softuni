from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kursov_proekt.orders.models import OrderItems, Orders
from kursov_proekt.product.models import Product, ProductSize


# Create your views here.




class DashboardProductCarts(ListView):
    model = Orders
    template_name = 'shop-details/shopping-cart.html'
    permission_classes = [IsAuthenticated]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        # Вземаме поръчките, които не са завършени (status=False) и принадлежат на текущия потребител
        valid_orders = Orders.objects.filter(status=False, profile_id=self.request.user.id)

        # Вземаме елементите от поръчката, които са свързани с валидните поръчки
        order_items = OrderItems.objects.filter(order__in=valid_orders)

        product_data = []

        # Обработваме всяка поръчка поотделно
        for item in order_items:
            product = item.product
            size = item.size
            count = item.quantity

            # Вземаме общата цена за продукта с размер
            total_price = product.price * count

            # Вземаме максималното количество за конкретния размер на продукта
            max_quantity = size.stock_quantity  # използваме stock_quantity от ProductSize

            product_data.append({
                'product': product,
                'size': size,
                'count': count,
                'total_price': total_price,
                'max_quantity': max_quantity  # добавяме max_quantity за съответния размер
            })

        # Пращаме данни към шаблона
        context['product_data'] = product_data

        return context