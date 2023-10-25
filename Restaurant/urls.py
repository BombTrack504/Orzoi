from django.urls import path
from . import views
from accounts import views as AccountViews
urlpatterns = [
    path('', AccountViews.Restaurantdashboard, name='Restaurant'),
    path('profile/', views.Restaurant_profile, name='Restaurant_profile'),
]
