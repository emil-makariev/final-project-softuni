from django.urls import path

from kursov_proekt.product import views

urlpatterns = (
    path('all-products/', views.DashboardProducts.as_view(), name='all-products'),
    path('create-products/', views.CreateProducts.as_view(), name='create-product'),
)