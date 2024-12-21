from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, FormView

from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import  ContactForm
from .models import Product, Wishlist, WishlistItem
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect

from ..accounts.models import Profile


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


class ToggleWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Проверяваме дали продуктът вече е в wishlist-а
        wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()

        if wishlist_item:
            # Ако продуктът е в wishlist, го премахваме
            wishlist_item.delete()
            return Response({'message': 'Product removed from wishlist'}, status=200)
        else:
            # Ако продуктът не е в wishlist, го добавяме
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            return Response({'message': 'Product added to wishlist'}, status=201)


class WishlistView(ListView):
    model = WishlistItem
    template_name = 'shop-details/wishlist.html'  # Тук ще показваме данните в този HTML шаблон
    context_object_name = 'wishlist_items'  # Това ще бъде името на променливата, която ще използваме в шаблона
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Вземаме всички елементи от wishlist-а на текущия потребител
        return WishlistItem.objects.filter(wishlist__user=self.request.user)


@method_decorator(login_required, name='dispatch')
class RemoveFromWishlistView(View):
    def post(self, request, item_id):
        try:
            # Изтриваме елемента от wishlist-а
            wishlist_item = WishlistItem.objects.get(id=item_id, wishlist__user=request.user)
            wishlist_item.delete()
            return JsonResponse({'success': True})
        except WishlistItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found or not in your wishlist.'})

def about_us(request):
    return render(request, 'shop-info/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Записва формата в базата данни
            return redirect('success')  # Пренасочва към страница за успех (може да създадеш такава)
    else:
        form = ContactForm()

    return render(request, 'shop-details/contact.html', {'form': form})

def success(request):
    return render(request, 'shop-details/success.html')