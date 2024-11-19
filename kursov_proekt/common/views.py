from django.shortcuts import render
from django.views.generic import ListView

from kursov_proekt.product.models import Product


# Create your views here.

class HomePage(ListView):
    model = Product
    template_name = 'common/index.html'

