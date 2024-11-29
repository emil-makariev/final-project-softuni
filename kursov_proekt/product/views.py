from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from kursov_proekt.product.forms import CreateProduct
from kursov_proekt.product.models import Product, Category
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

        if category_name:
            try:
                if brand_name == queryset[0].brand:
                    print('YAAAS')
                else:
                    print('adadada')
                queryset = queryset.filter(category__name=category_name)
            except Category.DoesNotExist:
                queryset = queryset.none()

        if brand_name:
            try:
                queryset = queryset.filter(brand=brand_name)
            except Exception as e:
                print(f"Error occurred: {e}")

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            products_data = context['object_list']
            serialized_data = ProductSerializer(products_data, many=True).data

            return JsonResponse({'products': serialized_data})

        return super().render_to_response(context, **response_kwargs)


class CreateProducts(CreateView):
    form_class = CreateProduct
    model = Product
    template_name = 'products/create-product.html'
    success_url = reverse_lazy('all-products')
    permission_required = 'product.can_create_products'


class UpdateProduct(UpdateView):
    pass