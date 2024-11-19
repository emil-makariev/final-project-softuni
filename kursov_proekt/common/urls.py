from django.urls import path

from kursov_proekt.common.views import HomePage

urlpatterns = (
    path('', HomePage.as_view(), name='common'),
)