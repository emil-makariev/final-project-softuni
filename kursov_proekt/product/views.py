from django.contrib.auth.decorators import permission_required
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




class CreateProducts(CreateView):
    form_class = CreateProduct
    model = Product
    template_name = 'products/create-product.html'
    success_url = reverse_lazy('all-products')
    permission_required = 'product.can_create_products'  # Specify the permission




class UpdateProduct(UpdateView):
    pass