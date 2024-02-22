from django.shortcuts import render
from django.http import HttpResponse

from Restaurant.models import Restaurant

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

# session for user lat and lng


def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat

    elif 'lat' in request.GET:
        lat = request.session['lat']
        lng = request.session['lng']
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

        restaurants = Restaurant.objects.filter(user_profile__location__distance_lte=(pnt, D(km=100))
                                                ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for r in restaurants:
            r.kms = round(r.distance.km, 1)
    else:
       # Retrieve approved and active restaurants limited to 6
        restaurants = Restaurant.objects.filter(
            is_approved=True, user__is_active=True)[:6]

    # Render the 'home.html' template and pass the restaurants as part of the context

    return render(request, 'home.html', {'restaurants': restaurants})
    # context = {'restaurants': restaurants}
