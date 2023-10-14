from django.shortcuts import render, redirect
from django.http import HttpResponse

from Restaurant.forms import RestaurantForm
from . forms import UserForm
from .models import User, UserProfile
from django.contrib import messages
# Create your views here.


def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # User.save()

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            messages.success(
                request, 'Your account has been created. Successfully !')
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerRestaurant(request):
    if request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        R_form = RestaurantForm(request.POST, request.FILES)

        if form.is_valid() and R_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.RESTAURANT
            user.save()
            Restaurant = R_form.save(commit=False)
            Restaurant.user = user
            user_profile = UserProfile.objects.get(user=user)
            Restaurant.user_profile = user_profile
            Restaurant.save()
            messages.success(
                request, 'Your account has been registered successfully! Please wait fot the approval')
            return redirect('registerRestaurant')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        R_form = RestaurantForm()

    context = {
        'form': form,
        'R_form': R_form,
    }
    return render(request, 'accounts/registerRestaurant.html', context)
