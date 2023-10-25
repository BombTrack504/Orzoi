from django.shortcuts import render


def Restaurant_profile(request):
    return render(request, 'Restaurant/Restaurant_profile.html')
