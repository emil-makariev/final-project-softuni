import json
from decimal import Decimal
from collections import defaultdict

from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from rest_framework.permissions import IsAuthenticated


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from kursov_proekt.orders.forms import BillingDetailsForm
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
            max_quantity = size.max_size  # Assuming you have stock_quantity in ProductSize
            price_for_a_singe_product = product.price

            product_data.append({
                'product': product,
                'size': size,
                'count': total_quantity,
                'size_text': size.size,
                'total_price': total_price,
                'max_quantity': max_quantity,  # Add max_quantity to the data
                'price_for_a_singe_product': price_for_a_singe_product,
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
            a = size.max_size

            print('Naslagvame')

            print(f"Max Quantity: {a}")
            a -= int(data['quantity'])
            print(f"Needed Quantity: {a}")
            size.stock_quantity = a
            print(f"Ensuring if this is the needed quantity: {size.stock_quantity}")
            print('-----------------------------------------------------------------------------------------------')

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

        print('Vadime')
        a = size.max_size
        print(f"Max Quantity: {a}")
        a -= int(data['quantity'])
        print(f"Needed Quantity: {a}")
        size.stock_quantity = a
        size.save()
        print(f"Ensuring if this is the needed quantity: {size.stock_quantity}")
        print('-----------------------------------------------------------------------------------------------')

        order_item.delete()



        total_price = 0
        for item in order.orders.all():
            total_price += item.product.get_discounted_price()

        order.total_price = total_price
        order.save()

        return JsonResponse({'status': 'success', 'message': 'Item removed from order'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def update_cart_total(request):
    if request.user.is_authenticated:
        # Вземаме поръчката на потребителя, която е в процес
        order = Orders.objects.get(profile=request.user.profile, status=False)

        # Изчисляваме общата цена чрез преминаване през всички артикули в поръчката
        total_price = sum(item.product.price * item.size.stock_quantity for item in order.orders.all())

        return JsonResponse({
            'status': 'success',
            'total_price': total_price
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})


@csrf_exempt
def remove_product_from_order(request):
    print('a')
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

            # Вземаме поръчката на потребителя
            user = request.user
            order = get_object_or_404(Orders, profile=user.profile, status=False)  # Поръчката, която не е завършена

            # Проверяваме дали продуктът с този размер съществува в поръчката
            order_items = OrderItems.objects.filter(order=order, product=product, size=size)

            if not order_items.exists():
                return JsonResponse({'status': 'error', 'message': 'Product with this size not found in order'}, status=400)

            # Преброяваме всички поръчки с този продукт и размер
            total_quantity_to_remove = order_items.count()

            # Премахваме всички такива продукти от поръчката
            order_items.delete()

            # Възстановяваме наличността на продукта в склада
            size.stock_quantity += total_quantity_to_remove  # Добавяме количеството обратно към наличността
            size.save()

            # Намаляваме общата цена на поръчката със стойността на премахнатите продукти
            product_price = product.get_discounted_price()
            order.total_price -= product_price * total_quantity_to_remove
            order.save()

            return JsonResponse({'status': 'success', 'message': 'Product removed from order successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


class FinalizeOrder(FormView):
    template_name = 'shop-details/checkout.html'
    form_class = BillingDetailsForm

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        order = get_object_or_404(Orders, profile__pk=pk)

        # Вземаме всички OrderItems за поръчката
        order_items = OrderItems.objects.filter(order=order)

        # Събиране на групираните продукти по категория и размер
        grouped_items = {}
        for item in order_items:
            product = item.product
            size = item.size
            category = product.category.name.lower()

            if category not in grouped_items:
                grouped_items[category] = {}

            if size not in grouped_items[category]:
                grouped_items[category][size] = {
                    'product': product,
                    'quantity': 0,
                    'total_price': Decimal('0.00')
                }

            # Увеличаване на количеството и цената
            grouped_items[category][size]['quantity'] += 1
            grouped_items[category][size]['total_price'] += product.get_discounted_price()

        context = super().get_context_data(**kwargs)
        context['order'] = order
        context['grouped_items'] = grouped_items
        return context

    def form_valid(self, form):
        # Получаваме поръчката по id
        order = self.get_object()

        # Актуализиране на num_of_times_purchased за всеки продукт в поръчката
        for order_item in order.order_items.all():
            product = order_item.product
            product.num_of_times_purchased += order_item.quantity
            product.save()

            # Проверка дали продуктът има размери
            if product.sizes.all().count() > 0:
                # Проверка дали всички размери на продукта имат stock_quantity == 0
                all_sizes_out_of_stock = product.sizes.all().filter(stock_quantity__gt=0).count() == 0

                # Ако всички размери са извън наличност, задаваме is_active = False
                if all_sizes_out_of_stock:
                    product.is_active = False
                    product.save()

        # Премахваме всички OrderItem-и за поръчката
        order.order_items.all().delete()

        # Може да добавите каквито действия искате след като поръчката е успешно обработена, например изпращане на имейл.

        # Пренасочваме към success страница
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('thank_you')

def after(request):
    return render(request, context=None, template_name='shop-details/after-purchesing.html')

