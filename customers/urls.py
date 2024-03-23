from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.Customerdashboard, name='customer'),
    path('profile/', views.customerprofile, name='customerprofile'),
]
