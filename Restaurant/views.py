from django.shortcuts import get_object_or_404, redirect, render

from .models import Restaurant

from Restaurant.forms import RestaurantForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_Restaurant


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
