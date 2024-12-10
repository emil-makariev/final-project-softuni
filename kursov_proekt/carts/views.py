import json
from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from rest_framework.permissions import IsAuthenticated


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from kursov_proekt.orders.models import OrderItems, Orders
from django.contrib.auth.decorators import login_required

from kursov_proekt.product.models import Product, ProductSize


class DashboardProductCarts(ListView):
    model = Orders
    template_name = 'shop-details/shopping-cart.html'
    permission_classes = [IsAuthenticated]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        # Get the orders that are not completed (status=False) and belong to the current user
        valid_orders = Orders.objects.filter(status=False, profile_id=self.request.user.id)

        # Get the order items related to the valid orders
        order_items = OrderItems.objects.filter(order__in=valid_orders)

        product_count = defaultdict(int)

        # Group products by product and size, and calculate the total quantity for each group
        for item in order_items:
            product = item.product
            size = item.size
            product_count[(product, size)] += 1

        product_data = []

        # For each product-size combination, get the total price and max stock quantity
        for (product, size), total_quantity in product_count.items():
            total_price = product.price * total_quantity
            max_quantity = size.stock_quantity  # Assuming you have stock_quantity in ProductSize

            product_data.append({
                'product': product,
                'size': size,
                'count': total_quantity,
                'size_text': size.size,
                'total_price': total_price,
                'max_quantity': max_quantity  # Add max_quantity to the data
            })
            print(product.id)

        context['product_data'] = product_data
        context['user_id'] = self.request.user.id

        return context


@csrf_exempt
def add_to_order(request):
    if request.method == 'POST':
        try:
            # Четене на JSON данни от тялото на POST заявката
            data = json.loads(request.body)

            # Извличане на product_id и size_id от JSON
            product_id = data.get('product_id')
            size_id = data.get('size_id')

            # Проверка за наличие на необходимите данни
            if not product_id or not size_id:
                return JsonResponse({'status': 'error', 'message': 'Missing product or size data'}, status=400)

            # Проверка за наличността на продукта и размера
            product = get_object_or_404(Product, id=product_id)
            size = get_object_or_404(ProductSize, id=size_id, product=product)

            # Вземаме или създаваме поръчка за потребителя
            user = request.user
            order, created = Orders.objects.get_or_create(
                profile=user.profile,
                status=False  # Статус "False" означава, че поръчката не е завършена
            )

            # Проверка дали има достатъчно наличност за продукта за даден размер
            if size.stock_quantity <= 0:
                return JsonResponse({'status': 'error', 'message': 'Not enough stock for this product'}, status=400)

            # Създаваме нов запис в OrderItems за всяко добавяне
            order_item = OrderItems.objects.create(
                order=order,
                product=product,
                size=size
            )



            price = product.get_discounted_price()  # Без да използваме quantity
            size.stock_quantity -= 1  # Възстановяваме наличността
            if size.stock_quantity == 1:
                size.stock_quantity -= 1
            size.save()

            order.total_price += price
            order.save()

            return JsonResponse({'status': 'success', 'message': 'Item added to order', 'order_item_id': order_item.id})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def remove_from_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            size_id = data.get('size_id')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        if not product_id or not size_id:
            return JsonResponse({'status': 'error', 'message': 'Missing product or size data'}, status=400)

        # Извличаме продукта и размера
        product = get_object_or_404(Product, id=product_id)
        size = get_object_or_404(ProductSize, id=size_id)

        # Проверка дали има достатъчно наличност за продукта за даден размер

        # Вземаме поръчката за текущия потребител
        user = request.user
        order = Orders.objects.get(profile=user.profile, status=False)

        # Намираме артикула в поръчката, като търсим по продукт и размер
        order_item = OrderItems.objects.filter(order=order, product=product, size=size).first()

        if not order_item:
            return JsonResponse({'status': 'error', 'message': 'Item not found in the order'}, status=404)

        # Премахваме артикула от количката
        order_item.delete()

        # Актуализираме наличността на размера
        size.stock_quantity += 1  # Възстановяваме наличността
        size.save()

        # Актуализираме цената на поръчката
        # Пресмятаме новата обща цена като вземем всички артикули в поръчката
        total_price = 0
        for item in order.orders.all():
            total_price += item.product.get_discounted_price()

        order.total_price = total_price
        order.save()

        return JsonResponse({'status': 'success', 'message': 'Item removed from order'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



def update_cart_total(request):
    if request.user.is_authenticated:
        order = Orders.objects.get(user=request.user, status='in_cart')
        total_price = sum(item.product.price * item.quantity for item in order.items.all())

        return JsonResponse({
            'status': 'success',
            'total_price': total_price
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})


class FinalizeOrder(ListView):
    model = Orders
    template_name = 'shop-details/checkout.html'
    success_url = reverse_lazy('common')


