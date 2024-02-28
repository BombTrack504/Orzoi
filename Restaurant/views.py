from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .models import Restaurant, OpeningHour

from Restaurant.forms import RestaurantForm, OpeningHourForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages

from django.http import HttpResponse, JsonResponse

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_Restaurant

from menu.models import FoodItem, Category

from menu.forms import CategoryForm, FoodItemForm

from django.template.defaultfilters import slugify


def get_restaurant(request):
    restaurant = Restaurant.objects.get(user=request.user)
    return restaurant


# Ensure the user is logged in. If not, redirect to the login page.
@login_required(login_url='login')
# Check if the user passes the 'check_role_Restaurant' test.
# This test can verify the user's role, and if it fails, it returns a 403 Forbidden response.
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
            # Print form errors for debugging purposes
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
@user_passes_test(check_role_Restaurant)
def menu_builder(request):
    restaurant = Restaurant.objects.get(user=request.user)
    categories = Category.objects.filter(
        restaurant=restaurant).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'restaurant/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)
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
@user_passes_test(check_role_Restaurant)
def add_category(request):
    if request.method == 'POST':
        # Create a CategoryForm instance and bind it with POST data
        form = CategoryForm(request.POST)

        if form.is_valid():
            # If the form data is valid, save it as a new Category instance
            category = form.save(commit=False)
            category.restaurant = Restaurant.objects.get(user=request.user)
            # Capitalize the category name for uniformity
            category.category_name = form.cleaned_data['category_name'].title()
            category.save()  # category id will be generated
            category.slug = slugify(
                # category name - slug id
                form.cleaned_data['category_name']) + '-' + str(category.id)
            category.save()
            messages.success(request, 'Category added Successfully!')
            # Redirect to the menu_builder view
            return redirect('menu_builder')
        else:
            # Handle form errors, e.g., log or display errors
            print(form.errors)
    else:
        # Create an empty form instance for adding a new category
        form = CategoryForm()

    # Prepare the context for rendering the 'add_category' template with the form
    context = {'form': form}
    return render(request, 'restaurant/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)
def edit_category(request, pk=None):
    # Fetch the Category instance based on the provided primary key
    category_obj = get_object_or_404(Category, pk=pk)

    # Assign a default instance of the CategoryForm
    form = CategoryForm(request.POST or None, instance=category_obj)

    if request.method == 'POST':

        if form.is_valid():
            # Update category details if the form data is valid
            category = form.save(commit=False)
            # Assign the restaurant to the updated category
            category.restaurant = Restaurant.objects.get(user=request.user)
            # Generate the slug based on the updated category name and ID
            category.slug = slugify(
                form.cleaned_data['category_name']) + '-' + str(category.id)
            # Capitalize the category name for uniformity
            category.category_name = form.cleaned_data['category_name'].title()
            form.save()  # Save the updated category instance
            messages.success(request, 'Category updated successfully!')
            # Redirect to the menu_builder view
            return redirect('menu_builder')
        else:
            # Handle form errors, e.g., log or display errors
            print(form.errors)

    # Prepare the context for rendering the 'edit_category' template with form and category details
    context = {'form': form, 'category': category_obj}
    return render(request, 'restaurant/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)
def add_food(request):
    form = FoodItemForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        # If it's a POST request, process the form data
        if form.is_valid():
            # If form data is valid, save it as a new FoodItem instance
            food = form.save(commit=False)
            # Assign the restaurant using get_object_or_404 for safety
            food.restaurant = get_object_or_404(Restaurant, user=request.user)
            # Generate the slug based on the food title
            food.save()
            food.slug = slugify(
                form.cleaned_data['food_title'])+'-'+str(food.id)
            food.save()  # Save the FoodItem instance
            # Display success message upon successful addition
            messages.success(request, 'Food item added successfully!')
            # Redirect to the specific category page after adding the food item
            return redirect('foodItems_by_category', food.category.id)
        else:
            # If form data is invalid, display an error message
            messages.error(
                request, 'Failed to add food item. Please check the form.')

    # Filter the category queryset based on the logged-in user's restaurant
    form.fields['category'].queryset = Category.objects.filter(
        restaurant=get_restaurant(request))

    # Prepare the context for rendering the 'add_food' template with the form
    context = {'form': form}
    return render(request, 'restaurant/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)
def edit_food(request, pk=None):
    # Fetch the FoodItem instance based on the provided primary key
    food = get_object_or_404(FoodItem, pk=pk)

    # Process the form data for updates if it's a POST request
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            # Update food details if the form data is valid
            food = form.save(commit=False)
            food.restaurant = get_object_or_404(Restaurant, user=request.user)
            # Generate the slug based on the updated food title
            food.slug = slugify(form.cleaned_data['food_title'])
            form.save()  # Save the updated food instance
            messages.success(request, 'Food Item updated successfully!')
            return redirect('foodItems_by_category', food.category.id)
        else:
            # Handle form errors, e.g., log or display errors
            print(form.errors)   # Temporary: Print form errors to console
    else:
        # If it's a GET request, populate the form with the existing food item data
        form = FoodItemForm(instance=food)
        # Filter the category queryset based on the logged-in user's restaurant
        form.fields['category'].queryset = Category.objects.filter(
            restaurant=get_restaurant(request))
     # Prepare the context for rendering the template with the form and food item details
    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'restaurant/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)
def delete_food(request, pk=None):
    # Get the specific FoodItem instance using the provided primary key.
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()  # Delete the retrieved FoodItem instance.
    # Display a success message to the user indicating successful deletion.
    messages.success(request, 'Food item has been deleted successfully!')
    # Redirect the user to the 'foodItems_by_category' view
    return redirect('foodItems_by_category', food.category.id)


def opening_hour(request):
    opening_hour = OpeningHour.objects.filter(
        restaurant=get_restaurant(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hour': opening_hour,
    }
    return render(request, 'restaurant/opening_hour.html', context)


def add_opening_hour(request):
    # handling the data and save them inside database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')

            # print(day, from_hour, to_hour, is_closed)

            try:
                hour = OpeningHour.objects.create(restaurant=get_restaurant(
                    request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id,
                                    'day': day.get_day_display(), 'is_closed': 'closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id,
                                    'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': to_hour}
                # response = {'status': 'success'}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour +
                            ' - '+to_hour+' already exist for this day!'}
                return JsonResponse(response)
        else:
            HttpResponse('invalid request')


def remove_opening_hour(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})
