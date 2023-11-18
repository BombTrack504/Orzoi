from django.shortcuts import get_object_or_404, redirect, render

from .models import Restaurant

from Restaurant.forms import RestaurantForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_Restaurant

from menu.models import FoodItem, Category

from menu.forms import CategoryForm, FoodItemForm

from django.template.defaultfilters import slugify


def get_restaurant(request):
    restaurant = Restaurant.objects.get(user=request.user)
    return restaurant


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def Restaurant_profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)  # fetch data
    restaurant = get_object_or_404(Restaurant, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile)
        Restaurant_form = RestaurantForm(
            request.POST, request.FILES, instance=restaurant)

        if profile_form.is_valid() and Restaurant_form.is_valid():
            profile_form.save()
            Restaurant_form.save()
            messages.success(request, 'settings Updated. ')
            return redirect('Restaurant_profile')

        else:
            print(profile_form.errors)
            print(Restaurant_form.errors)
    else:
        profile_form = UserProfileForm(
            instance=profile)  # load existance content
        Restaurant_form = RestaurantForm(instance=restaurant)

    context = {
        'profile_form': profile_form,
        'Restaurant_form': Restaurant_form,
        "profile": profile,
        'restaurant': restaurant,
    }

    return render(request, 'Restaurant/Restaurant_profile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def menu_builder(request):
    restaurant = Restaurant.objects.get(user=request.user)
    categories = Category.objects.filter(
        restaurant=restaurant).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'restaurant/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def foodItems_by_category(request, pk=None):

    # Assuming 'Restaurant' and 'FoodItem' models are imported correctly
    restaurant = Restaurant.objects.get(user=request.user)

    # Retrieve the Category object based on the provided primary key (pk)
    category_obj = get_object_or_404(Category, pk=pk)

    # Filter FoodItems based on the retrieved category and restaurant
    fooditems = FoodItem.objects.filter(
        restaurant=restaurant, category=category_obj)

    context = {
        'fooditems': fooditems,
        'category': category_obj,
    }

    # Return the response, passing the category_obj and fooditems to the template
    return render(request, 'restaurant/foodItems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.restaurant = Restaurant.objects.get(user=request.user)
            category.slug = slugify(category_name)+'-'+str(category.id)
            category.category_name = category_name.title()
            form.save()
            messages.success(request, 'Category added Successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }
    return render(request, 'restaurant/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def edit_category(request, pk=None):
    # Use 'Category' instead of 'category' in get_object_or_404
    category_obj = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category_obj)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.restaurant = Restaurant.objects.get(user=request.user)
            category.slug = slugify(category_name) + '-' + str(category.id)
            category.category_name = category_name.title()
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category_obj)
    context = {
        'form': form,
        'category': category_obj,
    }
    return render(request, 'restaurant/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)

        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.restaurant = Restaurant.objects.get(user=request.user)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food item added Successfully!')
            return redirect('foodItems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(
            restaurant=get_restaurant(request))
    context = {
        'form': form,
    }
    return render(request, 'restaurant/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def edit_food(request, pk=None):
    # Use 'Category' instead of 'category' in get_object_or_404
    food = get_object_or_404(FoodItem, pk=pk)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.restaurant = Restaurant.objects.get(user=request.user)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Item updated successfully!')
            return redirect('foodItems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(
            restaurant=get_restaurant(request))
    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'restaurant/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food item has been deleted successfully!')
    return redirect('foodItems_by_category', food.category.id)
