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


        best_sellers = Product.objects.filter(num_of_times_purchased__gt=5).order_by('-num_of_times_purchased')[:3]
        new_arrivals = Product.objects.all().order_by('-created_at')[:3]


        # Add best_sellers to the context
        context['best_sellers'] = best_sellers
        context['new_arrivals'] = new_arrivals

        return context
