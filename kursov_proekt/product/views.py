from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.generic import ListView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from kursov_proekt.product.models import Product
from kursov_proekt.product.serializers import ProductSerializer


# Create your views here.

class DashboardProducts(ListView):
    model = Product
    template_name = 'common/shop.html'
    paginate_by = 12
