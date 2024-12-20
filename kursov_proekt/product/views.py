from _decimal import Decimal
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, FormView, DetailView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kursov_proekt.common.models import Wishlist, WishlistItem
from kursov_proekt.orders.models import Orders, OrderItems
from kursov_proekt.orders.serializer import OrderItemsSerializer
from kursov_proekt.product.forms import CreateProduct, SearchForm, EditProductForm
from kursov_proekt.product.models import Product, Category, ProductSize, Accessory
from kursov_proekt.product.serializers import ProductSerializer



class DashboardProducts(ListView):
    model = Product
    template_name = 'common/shop.html'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)  # Само активни продукти

        category_name = self.request.GET.get('category')
        brand_name = self.request.GET.get('brand')
        price_name = self.request.GET.get('price')
        size = self.request.GET.get('size')
        color = self.request.GET.get('color')
        size_sort = self.request.GET.get('sort-price')
        search_param = self.request.GET.get('search_data')

        if search_param:
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
                # Filter products by the size in the related ProductSize model
                queryset = queryset.filter(sizes__size=size, sizes__stock_quantity__gt=0)
            except Exception as e:
                print(f"Error occurred: {e}")

        if color:
            try:
                queryset = queryset.filter(color=color)
            except Exception as e:
                print(f"Error occurred: {e}")
        if size_sort:
            if size_sort == 'Low To High':
                print('asasasas')
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
        context['is_staff'] = self.request.user.has_perm('product.can_create_products')

        if self.request.user.is_authenticated:
            try:
                wishlist = Wishlist.objects.get(user=self.request.user)
                wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
                context['wishlist_item'] = wishlist_items
                wishlist_product_ids = [item.product.id for item in wishlist_items]
                context['wishlist_item_ids'] = wishlist_product_ids  # Добавяме само ID-та
            except Wishlist.DoesNotExist:
                context['wishlist_item'] = []  # No wishlist found for this user
                context['wishlist_item_ids'] = []  # Няма wishlist за този потребител
        else:
            context['wishlist_item'] = []  # No wishlist for anonymous users
            context['wishlist_item_ids'] = []  # Няма wishlist за анонимни потребители

        print(context['wishlist_item'])

        return context


class CreateProducts(PermissionRequiredMixin, CreateView):
    form_class = CreateProduct
    model = Product
    template_name = 'products/create-product.html'
    success_url = reverse_lazy('all-products')
    permission_required = 'product.can_create_products'

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy('common'))


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
        accessory = None
        if product.sizes.exists():
            if not size_name and product.category.name != 'accessories':  # Assuming 'accessories' doesn't need size
                return Response({"detail": "Size is required for this product."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # Fetch the size associated with the product by size name
                size = product.sizes.get(size=size_name)
                if size.stock_quantity - 1 < 0:
                    return Response({"detail": "Quantity for this product size is zero"}, status=status.HTTP_400_BAD_REQUEST)
            except ProductSize.DoesNotExist:
                return Response({"detail": "Size not found."}, status=status.HTTP_404_NOT_FOUND)
        elif product.accessory:
            try:
                accessory = product.accessory
                if accessory.stock_quantity - 1 < 0:
                    return Response({"detail": "Quantity for this product size is zero"}, status=status.HTTP_400_BAD_REQUEST)
            except Accessory.DoesNotExist:
                return Response({"detail": "Accessory not found."}, status=status.HTTP_404_NOT_FOUND)


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
            size=size,
            accessory=accessory,
        )

        if size:
            if size.stock_quantity > size.max_size:
                size.stock_quantity = size.max_size
            else:
                size.stock_quantity -= 1
                size.save()

        elif accessory:
            if accessory.stock_quantity > accessory.max_quantity_accessory:
                accessory.stock_quantity = accessory.max_quantity_accessory
            else:
                accessory.stock_quantity -= 1
                accessory.save()

        # Update the total price of the order (Optional, if you need this logic)
        order.total_price += product.price  # Add product price (you might want to consider quantity)
        order.save()

        # Return a success response with the created order item data
        return Response({
            'detail': 'Product added to cart successfully.',
            'order_item': OrderItemsSerializer(order_item).data
        }, status=status.HTTP_201_CREATED)


    def get(self, request, *args, **kwargs):
        # Get the filtered products based on the request parameters
        products = Product.objects.filter(...)  # Your filtering logic

        product_data = []
        for product in products:
            sizes = [size.size for size in product.sizes.all()] if product.sizes.exists() else []
            product_data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'main_image': product.main_image.url,
                'sizes': sizes,  # Add the sizes here (empty if no sizes exist)
            })

        return Response({'products': product_data})


def get_product_sizes(request, pk):
    try:
        product = Product.objects.get(id=pk)  # Вземаме продукта по ID
        # Филтрираме размера и количеството за продукта
        sizes = ProductSize.objects.filter(product=product)

        size_data = []
        for size in sizes:
            size_data.append({
                'size': size.size,
                'stock_quantity': size.stock_quantity,
                'is_available': size.stock_quantity > 0  # Проверяваме дали количеството е повече от 0
            })

        return JsonResponse({'sizes': size_data})

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


class ProductDetail(DetailView):
    template_name = 'shop-details/shop-details.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        category = product.category_id
        pk_product = product.pk

        context['similar_products'] = Product.objects.filter(is_active=True, category=category).exclude(id=product.id)
        context['pk_product'] = pk_product
        if self.request.user.is_authenticated:
            try:
                wishlist = Wishlist.objects.get(user=self.request.user)
                wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
                context['wishlist_item'] = wishlist_items
            except Wishlist.DoesNotExist:
                context['wishlist_item'] = []  # No wishlist found for this user
        else:
            context['wishlist_item'] = []  # No wishlist for anonymous users
        return context


class EditProductView(UpdateView):
    template_name = 'products/edit-product.html'
    model = Product
    form_class = EditProductForm
    success_url = reverse_lazy('common')
    permission_required = 'product.can_create_products'

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy('common'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = Category.objects.all()
        return context
