from django.shortcuts import render
from django.views.generic import ListView

from kursov_proekt.product.models import Product


# Create your views here.

class HomePage(ListView):
    model = Product
    template_name = 'common/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permissions = self.request.user.get_group_permissions()
        context['has_perm'] = True if 'product.can_create_products' in permissions else False
        return context
