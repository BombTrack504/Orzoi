from django.urls import path
from . import views

urlpatterns = [
    path('registerUser/', views.registerUser, name='registerUser'),
    path('registerRestaurant/', views.registerRestaurant,
         name='registerRestaurant'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myAccount/', views.myAccount, name='myAccount'),
    path('Customerdashboard/', views.Customerdashboard, name='Customerdashboard'),
    path('Restaurantdashboard/', views.Restaurantdashboard,
         name='Restaurantdashboard'),
]
