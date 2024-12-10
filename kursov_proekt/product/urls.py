from django.urls import path

from kursov_proekt.product import views

urlpatterns = (
    path('all-products/', views.DashboardProducts.as_view(), name='all-products'),
    path('create-products/', views.CreateProducts.as_view(), name='create-product'),
    path('add-to-cart/<int:pk>/', views.AddOrderItems.as_view(), name='add-to-cart'),
    path('get-sizes/<int:pk>/', views.get_product_sizes, name='get_product_sizes'),
)