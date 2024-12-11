from _decimal import Decimal
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, FormView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kursov_proekt.orders.models import Orders, OrderItems
from kursov_proekt.orders.serializer import OrderItemsSerializer
from kursov_proekt.product.forms import CreateProduct, SearchForm
from kursov_proekt.product.models import Product, Category, ProductSize
from kursov_proekt.product.serializers import ProductSerializer


# Create your views here.


class DashboardProducts(ListView):
    model = Product
    template_name = 'common/shop.html'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()

        category_name = self.request.GET.get('category')
        brand_name = self.request.GET.get('brand')
        price_name = self.request.GET.get('price')
        size = self.request.GET.get('size')
        color = self.request.GET.get('color')
        size_sort = self.request.GET.get('sort-price')
        search_param = self.request.GET.get('search_data')

        if search_param:
            print(search_param)
            try:
                queryset = queryset.filter(name__icontains=search_param)
            except Exception as e:
                print(f"Error occurred: {e}")

        if category_name:
            try:
                queryset = queryset.filter(category__name=category_name)
            except Category.DoesNotExist:
                queryset = queryset.none()

        if brand_name:
            try:
                queryset = queryset.filter(brand=brand_name)
            except Exception as e:
                print(f"Error occurred: {e}")

        if price_name:
            try:
                min_max_price = price_name.split('-')
                min_price = int(min_max_price[0])

                try:
                    max_price = int(min_max_price[1])
                except IndexError:
                    max_price = None
                except ValueError:
                    max_price = None

                if max_price is not None:
                    queryset = queryset.filter(price__gte=min_price, price__lt=max_price)
                else:
                    queryset = queryset.filter(price__gte=min_price)

            except Exception as e:
                print(f"Error occurred: {e}")

        if size:
            try:
                queryset = queryset.filter(size=size)
            except Exception as e:
                print(f"Error occurred: {e}")

        if color:
            try:
                queryset = queryset.filter(color=color)
            except Exception as e:
                print(f"Error occurred: {e}")
        if size_sort:
            if size_sort == 'Low To High':
                queryset = queryset.order_by('price')
            elif size_sort == 'High To Low':
                queryset = queryset.order_by('-price')

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            products_data = context['object_list']
            serialized_data = ProductSerializer(products_data, many=True).data
            search_query = self.request.GET.get('search-data', '')
            context['search_query'] = search_query

            return JsonResponse({'products': serialized_data})

        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_clothing'] = len(self.object_list.filter(category__name='clothing'))
        context['total_accessories'] = len(self.object_list.filter(category__name='accessories'))
        context['total_shoes'] = len(self.object_list.filter(category__name='shoes'))

        return context


class CreateProducts(CreateView):
    form_class = CreateProduct
    model = Product
    template_name = 'products/create-product.html'
    success_url = reverse_lazy('all-products')
    permission_required = 'product.can_create_products'


class UpdateProduct(UpdateView):
    pass


class AddOrderItems(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemsSerializer

    def post(self, request, *args, **kwargs):
        # Retrieve data from the request
        product_id = request.data.get('product_id')
        size_name = request.data.get('size')  # Retrieve the size name (e.g., 'XS')

        if not product_id:
            return Response({"detail": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the product from the database
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product has sizes
        size = None
        if product.sizes:
            if not size_name:
                return Response({"detail": "Size is required for this product."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Fetch the size associated with the product by size name
                size = product.sizes.get(size=size_name)  # Assuming the size field in ProductSize is 'name'
            except ProductSize.DoesNotExist:
                return Response({"detail": "Size not found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve or create the user's order (status=False means 'pending' order status)
        user = request.user  # Get the logged-in user
        profile = user.profile  # Assuming each user has a profile

        # Fetch or create the order
        order, created = Orders.objects.get_or_create(
            profile=profile,
            status=False  # Assuming False means 'pending' order status
        )

        # Create the order item
        order_item = OrderItems.objects.create(
            order=order,
            product=product,
            size=size  # Only associate size if the product has sizes
        )
        size.stock_quantity -= 1
        size.save()

        # Update the total price of the order (Optional, if you need this logic)
        order.total_price += Decimal(product.price)  # Add product price (you might want to consider quantity)
        order.save()

        # Return a success response with the created order item data
        return Response({
            'detail': 'Product added to cart successfully.',
            'order_item': OrderItemsSerializer(order_item).data
        }, status=status.HTTP_201_CREATED)


def get_product_sizes(request, pk):
    try:
        product = Product.objects.get(id=pk)  # Вземаме продукта по ID
        # Филтрираме размера и количеството за продукта
        sizes = ProductSize.objects.filter(product=product)

        size_data = []
        for size in sizes:
            # Добавяме информация за размера и количеството
            size_data.append({
                'size': size.size,
                'stock_quantity': size.stock_quantity,
                'is_available': size.stock_quantity > 0  # Проверяваме дали количеството е повече от 0
            })

        return JsonResponse({'sizes': size_data})

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)