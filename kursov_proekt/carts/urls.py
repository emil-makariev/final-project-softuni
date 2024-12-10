from django.urls import path

from kursov_proekt.carts import views

urlpatterns = (
    path('<int:pk>/', views.DashboardProductCarts.as_view(), name='all-products-carts'),
    path('add-to-order/', views.add_to_order, name='add_to_order'),
    path('remove-from-order/', views.remove_from_order, name='remove_from_order'),
    path('update-cart-total/', views.update_cart_total, name='update_cart_total'),
    path('check-out/<int:pk>/', views.FinalizeOrder.as_view(), name='check_out')
    # http://127.0.0.1:8000/carts/40/add-to-order/
)