from django.shortcuts import redirect, render
from django.http import HttpResponse

# from Restaurant.forms import ReviewForm
from Restaurant.forms import ReviewForm
from Restaurant.models import Restaurant, ReviewAndRating

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib import messages

from django.db.models import Avg, Count
from django.db import connection
# session for user lat and lng
from django.db.models.functions import Coalesce
from django.db.models import Value


def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat

    elif 'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat

    else:
        return None


def home(request):
    if get_or_set_current_location(request) is not None:
        # lat = request.GET.get('lat')
        # lng = request.GET.get('lng')

        pnt = GEOSGeometry('POINT(%s %s)' %
                           (get_or_set_current_location(request)))

        restaurants = Restaurant.objects.filter(user_profile__location__distance_lte=(pnt, D(
            km=10))).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
        for r in restaurants:
            r.kms = round(r.distance.km, 1)
    else:
        # Retrieve approved and active restaurants limited to 6
        restaurants = Restaurant.objects.filter(
            is_approved=True, user__is_active=True
        ).annotate(
            avg_rating=Coalesce(Avg('reviews__rating'), Value(0.0))
        ).order_by('-avg_rating')[:6]

        # Debugging: Print average ratings
        for restaurant in restaurants:
            print(restaurant.avg_rating)

    # Print the generated SQL query
    print(connection.queries)

    # Get the reviews
    reviews = None
    for restro in restaurants:
        reviews = ReviewAndRating.objects.filter(
            restaurant_id=restro.id, status=True)

    # Render the 'home.html' template and pass the restaurants as part of the context
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'home.html', context)


def submit_review(request, restaurant_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # Change 'restaurantid' to 'restaurant_id'
            review = ReviewAndRating.objects.get(
                user_id=request.user.id, restaurant_id=restaurant_id)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Thank You! Your review has been updated.')
                return redirect(url)
        except ReviewAndRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.restaurant_id = restaurant_id
                data.user_id = request.user.id
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                messages.success(
                    request, 'Thank You! Your review has been submitted.')
                return redirect(url)
            else:
                return HttpResponse("An error occurred. Please try again.")
    else:
        return HttpResponse("An error occurred. Please try again.")
