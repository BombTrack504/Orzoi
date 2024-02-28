from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.Restaurantdashboard, name='Restaurant'),

    path('profile/', views.Restaurant_profile, name='Restaurant_profile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/',
         views.foodItems_by_category, name='foodItems_by_category'),

    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/',
         views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/',
         views.delete_category, name='delete_category'),

    # Food item CRUD
    path('menu-builder/food/add/', views.add_food, name='add_food'),
    path('menu-builder/food/edit/<int:pk>/',
         views.edit_food, name='edit_food'),
    path('menu-builder/food/delete/<int:pk>/',
         views.delete_food, name='delete_food'),

    # opening hour CRUD
    path('opening-hour/',
         views.opening_hour, name='opening_hour'),
    path('opening-hour/add/',
         views.add_opening_hour, name='add_opening_hour'),
    path('opening-hour/remove/<int:pk>/',
         views.remove_opening_hour, name='remove_opening_hour'),
]
