from django.urls import path
from kursov_proekt.common import views
from kursov_proekt.common.views import HomePage, ToggleWishlistView, WishlistView, RemoveFromWishlistView

urlpatterns = (
    path('', HomePage.as_view(), name='common'),
    path('api/toggle-wishlist/<int:product_id>/', ToggleWishlistView.as_view(), name='toggle_wishlist'),
    path('product-wishlist/<int:pk>', WishlistView.as_view(), name='product-wishlist'),
    path('remove_from_wishlist/<int:item_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('about-us/', views.about_us, name='about-us'),
    path('contact/', views.contact, name='contacts'),
    path('success/', views.success, name='success'),  # Пример за страница за успех

)