from django.contrib.auth.views import LogoutView
from django.urls import path
from kursov_proekt.accounts import views

urlpatterns = (
    path('register/', views.CreateUserView.as_view(), name='register'),
    path('log-in/', views.LoginViewCustom.as_view(), name='log-in'),
    path('log-out/', LogoutView.as_view(), name='log-out'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('email-message/', views.email_message, name='email-message'),
    path('details-profile/<int:pk>', views.DetailsProfile.as_view(), name='details-profile'),
    path('edit-profile/<int:pk>', views.EditProfile.as_view(), name = 'edit-profile'),


)