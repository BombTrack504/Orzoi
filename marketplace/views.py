from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from menu.models import Category, FoodItem

from Restaurant.models import Restaurant
from django.db.models import Prefetch

from django.http import JsonResponse
from . models import FoodCart

from . context_processors import get_cart_counter,  get_cart_amt
from django.contrib.auth.decorators import login_required
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
