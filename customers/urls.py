from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.Customerdashboard, name='customer'),
    path('profile/', views.customerprofile, name='customerprofile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_details/<int:order_number>/',
         views.order_details, name='order_details'),
]
