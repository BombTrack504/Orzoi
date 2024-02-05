from django.shortcuts import render
from django.http import HttpResponse

from Restaurant.models import Restaurant


def home(request):
    # Retrieve approved and active restaurants limited to 6
    restaurants = Restaurant.objects.filter(
        is_approved=True, user__is_active=True)[:6]

    # Render the 'home.html' template and pass the restaurants as part of the context

    return render(request, 'home.html', {'restaurants': restaurants})
    # context = {'restaurants': restaurants}
