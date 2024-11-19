
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kursov_proekt.common.urls')),
    # path('product/', include('kursov_proekt.product.urls')),
    path('account/', include('kursov_proekt.accounts.urls')),
]
