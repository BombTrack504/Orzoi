from django.urls import path
from .import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('verify-khalti-payment/', views.verify_khalti_payment,
         name='verify_khalti_payment'),
]
