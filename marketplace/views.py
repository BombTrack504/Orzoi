from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from menu.models import Category, FoodItem

from django.shortcuts import redirect
from Restaurant.models import Restaurant, OpeningHour
from django.db.models import Prefetch

from django.http import JsonResponse
from . models import FoodCart

from django.http import HttpResponse
from . context_processors import get_cart_counter,  get_cart_amt
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from datetime import date
from django.utils import timezone
from datetime import datetime
# Create your views here.


def marketplace(request):
    restaurants = Restaurant.objects.filter(
        is_approved=True, user__is_active=True)
    res_count = len(restaurants)

    context = {
        'restaurants': restaurants,
        'res_count': res_count,

    }
    return render(request, 'marketplace/listings.html', context)


def restaurant_detail(request, restaurant_slug):
    restaurant_detail = get_object_or_404(
        Restaurant, restaurant_slug=restaurant_slug)

    # fooditems fk in category using related name (reverse lookup)
    categories = Category.objects.filter(
        restaurant=restaurant_detail).prefetch_related(
            Prefetch(
                'fooditems',
                queryset=FoodItem.objects.filter(is_available=True)
            )
    )

    opening_hour = OpeningHour.objects.filter(
        restaurant=restaurant_detail).order_by('day', '-from_hour')

    # check current day opening hour
    today_date = date.today()
    today = today_date.isoweekday()

    current_opening_hour = OpeningHour.objects.filter(
        restaurant=restaurant_detail, day=today)

    cart_items = (
        FoodCart.objects.filter(user=request.user)
        if request.user.is_authenticated
        else None
    )

    context = {
        key: value for key, value in [
            ('restaurant_detail', restaurant_detail),
            ('categories', categories),
            ('cart_items', cart_items),
            ('opening_hour', opening_hour),
            ('current_opening_hour', current_opening_hour),
            # Add more key-value pairs here if needed
        ]
    }
    return render(request, 'marketplace/restaurant_detail.html', context)


# Add to cart


def add_to_cart(request, food_id):
    if request.user.is_authenticated and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        try:
            fooditem = get_object_or_404(FoodItem, id=food_id)

            cart_item, created = FoodCart.objects.get_or_create(
                user=request.user, fooditem=fooditem,
                defaults={'quantity': 1}
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Increased the cart quantity',
                    'cart_counter': get_cart_counter(request),
                    'qty': cart_item.quantity,
                    'cart_amount': get_cart_amt(request)
                })

            return JsonResponse({
                'status': 'success',
                'message': 'Successfully Added the food to the cart',
                'cart_counter': get_cart_counter(request),
                'qty': cart_item.quantity,
                'cart_amount': get_cart_amt(request)
            })

        except FoodItem.DoesNotExist:
            return JsonResponse({
                'status': 'Failed',
                'message': 'This food does not exist!'
            })
    else:
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'login_required',
                'message': 'Please log in to continue'
            })
        else:
            return JsonResponse({
                'status': 'Failed',
                'message': 'Invalid request!'
            })


# decrease cart

def decrease_cart(request, food_id):
    if request.user.is_authenticated and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        try:
            fooditem = get_object_or_404(FoodItem, id=food_id)
            cart_item = FoodCart.objects.get(
                user=request.user, fooditem=fooditem)

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                cart_item.quantity = 0

            return JsonResponse({
                'status': 'success',
                'cart_counter': get_cart_counter(request),
                'qty': cart_item.quantity,
                'cart_amount': get_cart_amt(request)
            })

        except FoodItem.DoesNotExist:
            return JsonResponse({
                'status': 'Failed',
                'message': 'This food does not exist!'
            })
        except FoodCart.DoesNotExist:
            return JsonResponse({
                'status': 'Failed',
                'message': 'You do not have this item in your cart!'
            })

    else:
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'login_required',
                'message': 'Please log in to continue'
            })
        else:
            return JsonResponse({
                'status': 'Failed',
                'message': 'Invalid request!'
            })


# Empty cart handling
@login_required(login_url='login')
def cart(request):
    cart_items = FoodCart.objects.filter(
        user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        cart_item = get_object_or_404(FoodCart, user=request.user, id=cart_id)
        cart_item.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Cart item has been deleted!',
            'cart_counter': get_cart_counter(request),
            'cart_amount': get_cart_amt(request)
        })
    else:
        return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid request!'
        })


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # get restaurant ids that has the food item the user is looking for
        fetch_restaurants_by_fooditems = FoodItem.objects.filter(
            food_title__icontains=keyword, is_available=True,).values_list('restaurant', flat=True)
        # print(fetch_restaurants_by_fooditems)
        restaurants = Restaurant.objects.filter(
            Q(id__in=fetch_restaurants_by_fooditems) | Q(Restaurant_name__icontains=keyword, is_approved=True, user__is_active=True))
        # print(restaurants)

        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

            restaurants = Restaurant.objects.filter(Q(id__in=fetch_restaurants_by_fooditems) | Q(
                Restaurant_name__icontains=keyword, is_approved=True, user__is_active=True),
                user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for r in restaurants:
                r.kms = round(r.distance.km, 1)

        res_count = restaurants.count()
        context = {
            'restaurants': restaurants,
            'res_count': res_count,
            'source_location': address,
        }

        # print(address, latitude, longitude, radius)
        # return HttpResponse('search page')

        return render(request, 'marketplace/listings.html', context)
