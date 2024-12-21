import json
from decimal import Decimal
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import ListView, DetailView, FormView
from rest_framework.permissions import IsAuthenticated
import asyncio
from django.core.mail import send_mail
from asgiref.sync import sync_to_async
from django.http import HttpResponse, Http404

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from kursov_proekt import settings
from kursov_proekt.accounts.models import CustomBaseUser
from kursov_proekt.orders.forms import BillingDetailsForm
from kursov_proekt.orders.models import OrderItems, Orders
from django.contrib.auth.decorators import login_required

from kursov_proekt.product.models import Product, ProductSize, Accessory


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
        order_items_quantity = {}

        # Group products by product and size, and calculate the total quantity for each group
        for item in order_items:
            product = item.product
            size = item.size
            if size:
                product_key = (product, size.size)

                if product_key in order_items_quantity:
                    order_items_quantity[product_key] += 1
                else:
                    order_items_quantity[product_key] = 1
            elif product.accessory:
                if product in order_items_quantity:
                    order_items_quantity[product] += 1
                else:
                    order_items_quantity[product] = 1

            product_count[(product, size)] += 1

        product_data = []

        # For each product-size combination, get the total price and max stock quantity
        for (product, size), total_quantity in product_count.items():
            if size:
                # Получаваме максималното количество от продукта за този размер
                max_quantity = size.max_size
            else:
                max_quantity = product.accessory.max_quantity_accessory

            # Проверяваме дали има излишък
            if total_quantity > max_quantity:
                # Изчисляваме излишните количества
                excess_quantity = total_quantity - max_quantity


                # Поставяме в данните новото количество, което е равнo на max_quantity
                product_data.append({
                    'product': product,
                    'size': size,
                    'count': max_quantity,  # Слагаме само допустимото количество
                    'size_text': size.size if size else 'No Size',
                    'total_price': product.price * max_quantity,  # Обновяваме цената
                    'max_quantity': max_quantity,
                    'price_for_a_singe_product': product.price,
                })

                if total_quantity > max_quantity:
                    if size:
                        size.stock_quantity = 0
                        size.save()
                    else:
                        product.accessory.stock_quantity = 0
                        product.accessory.save()

                # Изтриваме само излишните продукти от количката
                excess_items = OrderItems.objects.filter(order__in=valid_orders, product=product, size=size)

                # Премахваме излишните продукти (които надвишават максималното количество)
                excess_items_to_delete = excess_items[:excess_quantity]

                for item in excess_items_to_delete:
                    item.delete()

            else:
                # Ако количеството не надвишава максималното, добавяме в данните без промени
                product_data.append({
                    'product': product,
                    'size': size,
                    'count': total_quantity,
                    'size_text': size.size if size else 'No Size',
                    'total_price': product.price * total_quantity,
                    'max_quantity': max_quantity,
                    'price_for_a_singe_product': product.price,
                })

        context['product_data'] = product_data
        context['user_id'] = self.request.user.id

        return context



@csrf_exempt
def add_to_order(request):
    if request.method == 'POST':
        try:
            # Четене на JSON данни от тялото на POST заявката
            data = json.loads(request.body)
            product_id = data.get('product_id')

            if not product_id:
                return JsonResponse({"detail": "Product ID is required."}, status=400)

            size_id = data.get('size_id')

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"detail": "Product not found."}, status=404)

            size = None
            accessory = None
            if product.sizes.exists():
                if not size_id and product.category.name != 'accessories':  # Assuming 'accessories' doesn't need size
                    return JsonResponse({"detail": "Size is required for this product."},status=400)
                try:
                    searched_size = ProductSize.objects.get(id=size_id)
                    size = product.sizes.get(size=searched_size.size)  # Assuming the size field in ProductSize is 'name'
                    if size.stock_quantity - 1 < 0:
                        return JsonResponse({'datail: Size out of stock'}, status=404)
                except ProductSize.DoesNotExist:
                    return JsonResponse({"detail": "Size not found."}, status=404)

            elif product.accessory:
                try:
                    accessory = product.accessory
                    if accessory.stock_quantity - 1 < 0:
                        return JsonResponse({'datail: Accessory out of stock'}, status=404)
                except Accessory.DoesNotExist:
                    return JsonResponse({"detail": "Accessory not found."}, status=404)


            # Вземаме или създаваме поръчка за потребителя
            user = request.user
            order, created = Orders.objects.get_or_create(
                profile=user.profile,
                status=False  # Статус "False" означава, че поръчката не е завършена
            )

            if size:
                if size.stock_quantity <= 0:
                    return JsonResponse({'status': 'error', 'message': 'Not enough stock for this product'}, status=400)
            elif accessory:
                if accessory.stock_quantity <= 0:
                    return JsonResponse({'status': 'error', 'message': 'Not enough stock for this product'}, status=400)

            # Създаваме нов запис в OrderItems за всяко добавяне
            order_item = OrderItems.objects.create(
                order=order,
                product=product,
                size=size,
                accessory=accessory,

            )

            price = product.get_discounted_price()

            if size:
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

                return JsonResponse(
                    {'status': 'success', 'message': 'Item added to order', 'order_item_id': order_item.id})


            elif accessory:
                a = accessory.max_quantity_accessory
                print('Naslagvame')

                print(f"Max Quantity: {a}")
                a -= int(data['quantity'])
                print(f"Needed Quantity: {a}")
                accessory.stock_quantity = a
                print(data['quantity'])
                print(accessory.stock_quantity)
                print(f"Ensuring if this is the needed quantity: {accessory.stock_quantity}")
                print('-----------------------------------------------------------------------------------------------')

                accessory.save()
                order.total_price += price
                order.save()

                return JsonResponse(
                    {'status': 'success', 'message': 'Item added to order', 'order_item_id': order_item.id})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def remove_from_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        if not product_id:
            return JsonResponse({"detail": "Product ID is required."}, status=400)

        size_id = data.get('size_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"detail": "Product not found."}, status=404)

        size = None
        accessory = None
        if product.sizes.exists():
            if not size_id and product.category.name != 'accessories':  # Assuming 'accessories' doesn't need size
                return JsonResponse({"detail": "Size is required for this product."}, status=400)
            try:
                searched_size = ProductSize.objects.get(id=size_id)
                size = product.sizes.get(size=searched_size.size)


            except ProductSize.DoesNotExist:
                return JsonResponse({"detail": "Size not found."}, status=404)

        elif product.accessory:
            try:
                accessory = product.accessory
            except Accessory.DoesNotExist:
                return JsonResponse({"detail": "Accessory not found."}, status=404)


        user = request.user
        order = Orders.objects.get(profile=user.profile, status=False)

        if size:
            size = get_object_or_404(ProductSize, id=size_id, product=product)
            order_item = OrderItems.objects.filter(order=order, product=product, size=size).first()
        else:
            order_item = OrderItems.objects.filter(order=order, product=product, accessory=accessory).first()

        if not order_item:
            return JsonResponse({'status': 'error', 'message': 'Product with this size not found in order'}, status=400)


        if size:
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
        else:
            print('Vadime')
            a = accessory.max_quantity_accessory
            print(f"Max Quantity: {a}")
            a -= int(data['quantity'])
            print(f"Needed Quantity: {a}")
            accessory.stock_quantity = a
            accessory.save()
            print(f"Ensuring if this is the needed quantity: {accessory.stock_quantity}")
            print('-----------------------------------------------------------------------------------------------')

            order_item.delete()

            total_price = 0
            for item in order.orders.all():
                total_price += item.product.get_discounted_price()

            order.total_price = total_price
            order.save()

            return JsonResponse({'status': 'success', 'message': 'Item removed from order'})



    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@sync_to_async
def get_authenticated_user(request):
    return request.user if request.user.is_authenticated else None


# Функция за извличане на поръчката на потребителя
@sync_to_async
def get_order_for_user(user):
    return Orders.objects.get(profile=user.profile, status=False)


@sync_to_async
def calculate_cart_total(order):
    total_price = 0.00
    for item in order.orders.all():
        total_price += item.product.price
    return total_price


async def update_cart_total(request):
    user = await get_authenticated_user(request)

    if user:
        # Получаваме поръчката за потребителя
        try:
            order = await get_order_for_user(user)
        except Orders.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No active order found for this user'})

        # Изчисляваме общата стойност на количката
        total_price = await calculate_cart_total(order)
        return JsonResponse({'status': 'success', 'total_price': total_price})

    return JsonResponse({'status': 'error', 'message': 'User not authenticated'})


@csrf_exempt
def remove_product_from_order(request):
    if request.method == 'POST':
        try:
            # Четене на JSON данни от тялото на POST заявката
            data = json.loads(request.body)

            # Извличане на product_id и size_id от JSON
            product_id = int(data.get('product_id'))
            size_id = data.get('size_id')
            accessories = None
            size=None

            if product_id and Accessory.objects.filter(product_id=product_id):
                accessories = get_object_or_404(Accessory, product_id=product_id)

            if (not product_id or not size_id) and accessories == None:
                return JsonResponse({'status': 'error', 'message': 'Missing product or size data'}, status=400)

            product = get_object_or_404(Product, id=product_id)
            user = request.user
            order = get_object_or_404(Orders, profile=user.profile, status=False)

            if product.category.name != 'accessories':
                size = get_object_or_404(ProductSize, id=size_id, product=product)
                order_items = OrderItems.objects.filter(order=order, product=product, size=size)
            else:
                order_items = OrderItems.objects.filter(order=order, product=product, accessory=accessories)

            if not order_items.exists():
                return JsonResponse({'status': 'error', 'message': 'Product with this size not found in order'}, status=400)

            # Преброяваме всички поръчки с този продукт и размер
            total_quantity_to_remove = order_items.count()

            # Премахваме всички такива продукти от поръчката
            order_items.delete()

            if product.category.name != 'accessories':
                size.stock_quantity += total_quantity_to_remove  # Добавяме количеството обратно към наличността
                size.save()
            else:
                accessories.stock_quantity += total_quantity_to_remove
                accessories.save()

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
    success_url = reverse_lazy('after_purchesing')

    def get_context_data(self, **kwargs):
        total_price_for_same_products = 0
        pk = self.kwargs['pk']
        order = get_object_or_404(Orders, profile__pk=pk, status=False)

        # Вземаме всички OrderItems за поръчката
        order_items = OrderItems.objects.filter(order=order)

        # Събиране на групираните продукти по категория и размер
        grouped_items = {}
        for item in order_items:
            product = item.product
            size = item.size
            accessory = item.accessory
            category = product.category.name.lower()

            if category not in grouped_items:
                grouped_items[category] = {}

            if size:
                if size not in grouped_items:
                    if size not in grouped_items[category]:
                        grouped_items[category][size] = {
                            'product': product,
                            'quantity': 0,
                            'total_price': 0.00
                        }
                grouped_items[category][size]['quantity'] += 1
                grouped_items[category][size]['total_price'] = product.price
                total_price_for_same_products += product.price

            if accessory:
                if accessory.product.name not in grouped_items[category]:
                    grouped_items[category][product.name] = {
                        'product': product,
                        'quantity': 0,
                        'total_price': 0.00,
                        'type': 'accessory'
                    }


                grouped_items[category][product.name]['quantity'] += 1
                grouped_items[category][product.name]['total_price'] = product.price
                total_price_for_same_products += product.price

        order.total_price = total_price_for_same_products

        context = super().get_context_data(**kwargs)
        context['order'] = order
        context['grouped_items'] = grouped_items
        context['total_price_for_same_products'] = total_price_for_same_products
        context['form'] = self.get_form()  # Add the form to the context
        return context

    def form_valid(self, form):
        # Get the order using the 'pk' from kwargs
        pk = self.kwargs['pk']
        order = get_object_or_404(Orders, profile__pk=pk, status=False)

        # Актуализиране на num_of_times_purchased за всеки продукт в поръчката
        for order_item in order.orders.all():
            product = order_item.product
            product.num_of_times_purchased += 1

            if product.sizes.exists():
                if product.sizes.all().count() > 0:
                    # Проверка дали всички размери на продукта имат stock_quantity == 0
                    all_sizes_out_of_stock = product.sizes.all().filter(stock_quantity__gt=0).count() == 0

                    # Ако всички размери са извън наличност, задаваме is_active = False
                    if all_sizes_out_of_stock:
                        product.is_active = False
                        product.save()

            else:
                if product.accessory.stock_quantity <= 0:
                    product.accessory.stock_quantity = 0
                    product.is_active = False
                    product.save()

        # Премахваме всички OrderItem-и за поръчката
        order.status = True
        order.save()
        order.orders.all().delete()

        # Пренасочваме към success страница
        form = form.save(commit=False)
        form.order_id = order.id
        form.save()

        return super().form_valid(form)


def after(request):
    return render(request, context=None, template_name='shop-details/after-purchesing.html')

