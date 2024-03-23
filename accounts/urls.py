from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.myAccount),
    path('registerUser/', views.registerUser, name='registerUser'),
    path('registerRestaurant/', views.registerRestaurant,
         name='registerRestaurant'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myAccount/', views.myAccount, name='myAccount'),
    path('Customerdashboard/', views.Customerdashboard, name='Customerdashboard'),
    path('Restaurantdashboard/', views.Restaurantdashboard,
         name='Restaurantdashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>', views.reset_password_validate,
         name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),

    path('Restaurant/', include('Restaurant.urls')),
    path('customer/', include('customers.urls')),

]
