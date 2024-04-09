from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import requests

from marketplace.models import FoodCart, Tax
from marketplace.context_processors import get_cart_amt
from menu.models import FoodItem

from .forms import OrderForm
from .models import Order, OrderedFood, Payment
import simplejson as json
from django.contrib.auth.decorators import login_required
from .utils import create_ord_num

from accounts.utils import send_notfication

from django.utils import timezone
from pytz import timezone as pytz_timezone
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.


@login_required(login_url='login')
def place_order(request):
    cart_items = FoodCart.objects.filter(
        user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

    restaurants_ids = []
    for i in cart_items:
        if i.fooditem.restaurant.id not in restaurants_ids:
            restaurants_ids.append(i.fooditem.restaurant.id)
    # print(restaurants_ids)

    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    a = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(
            pk=i.fooditem.id, restaurant_id__in=restaurants_ids)
        # print(fooditem, fooditem.restaurant.id)
        r_id = fooditem.restaurant.id
        if r_id in a:
            subtotal = a[r_id]
            subtotal += (fooditem.price * i.quantity)
            a[r_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            a[r_id] = subtotal
    # print(a)

        # calculate tax data
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})
        # print(tax_dict)
        total_data.update(
            {fooditem.restaurant.id: {str(subtotal): str(tax_dict)}})

    # print(total_data)

    subtotal = get_cart_amt(request)['subtotal']
    total_tax = get_cart_amt(request)['tax']
    grand_total = get_cart_amt(request)['grandtotal']
    tax_dict_data = get_cart_amt(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            ord = Order()
            ord.first_name = form.cleaned_data['first_name']
            ord.last_name = form.cleaned_data['last_name']
            ord.phone = form.cleaned_data['phone']
            ord.email = form.cleaned_data['email']
            ord.address = form.cleaned_data['address']
            ord.city = form.cleaned_data['city']
            ord.country = form.cleaned_data['country']
            ord.state = form.cleaned_data['state']
            ord.pin_code = form.cleaned_data['pin_code']
            ord.user = request.user
            ord.total = grand_total
            ord.tax_data = json.dumps(tax_dict_data)
            ord.total_data = json.dumps(total_data)
            ord.total_tax = total_tax
            ord.payment_method = request.POST['payment_method']
            ord.save()  # order id (order table pk is generated)
            ord.order_number = create_ord_num(ord.id)
            ord.restaurants.add(*restaurants_ids)
            ord.save()
            context = {
                'ord': ord,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)

            # Redirect to the same page after placing order
            # return redirect('place_order')
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')


@login_required(login_url='login')
def verify_khalti_payment(request):
    # check if the request is ajax or not
    if request.headers.get('X-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # Retrieve data from the frontend
        data = json.loads(request.body)
        order_number = data.get('order_number')
        amount = data.get('amount')
        token = data.get('token')
        headers = {
            # set this to your desired env variable
            'Authorization': 'Key test_secret_key_bba1c6b90747483ab475341d7fe54446',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'amount': amount,
            'token': token,
        }
        # request formated as mentioned in khalti docs
        response = requests.post(
            'https://khalti.com/api/v2/payment/verify/', headers=headers, data=data)
        verification_data = response.json()

        if verification_data['idx']:  # khalti sends idx when payment is successfull
            # Payment is successful
            ord = Order.objects.get(order_number=order_number)

            payment = Payment.objects.create(
                user=request.user,
                payment_method='Khalti',
                amount=amount/100,
                transaction_id=verification_data['idx'],
                # check the response for completed status
                status='Success' if verification_data['state']['name'] == 'Completed' else 'Pending'
            )

            # Convert created_at to Nepal time zone
            ord.created_at = timezone.localtime(
                ord.created_at, pytz_timezone('Asia/Kathmandu'))

            # Update purchase status
            ord.payment = payment
            ord.is_ordered = True
            ord.save()

            # move the cart items to ordered food model
            cart_items = FoodCart.objects.filter(user=request.user)
            for item in cart_items:
                o_food = OrderedFood()
                o_food.order = ord
                o_food.payment = payment
                o_food.user = request.user
                o_food.fooditem = item.fooditem
                o_food.quantity = item.quantity
                o_food.price = item.fooditem.price
                o_food.amount = item.fooditem.price * item.quantity
                o_food.save()

            # send order confirmation email to the customer
            mail_subject = 'thankyou'
            mail_template = 'orders/order_confirmation.html'
            ordered_food = OrderedFood.objects.filter(order=ord)
            context = {
                'user': request.user,
                'ord': ord,
                'to_email': ord.email,
                'ordered_food': ordered_food,
                'domain': get_current_site(request),
            }
            send_notfication(mail_subject, mail_template, context)

            # send order recived email to the restaurant
            mail_subject = 'You have received a new order.'
            mail_template = 'orders/order_received.html'
            to_emails = []
            for i in cart_items:
                if i.fooditem.restaurant.user.email not in to_emails:
                    to_emails.append(i.fooditem.restaurant.user.email)
            print('to_emails ==>', to_emails)
            context = {
                'ord': ord,
                'to_email':  to_emails,
            }
            send_notfication(mail_subject, mail_template, context)

            FoodCart.objects.filter(user=request.user).delete()

            return JsonResponse({'status': 'success'})

        else:
            # Payment failed
            return JsonResponse({'status': 'error', 'message': 'Payment verification failed'})

    else:
        # Handle invalid request method
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    try:
        ord = Order.objects.get(
            order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=ord)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(ord.tax_data)

        context = {
            'order': ord,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')


# @login_required(login_url='login')
# def payments(request):
#     # check if the request is ajax or not
#     if request.headers.get('X-requested-with') == 'XMLHttpRequest' and request.method == 'POST':

#         # store the payment details in the payment model
#         order_number = request.POST.get('order_number')
#         transaction_id = request.POST.get('transaction_id')
#         payment_method = request.POST.get('payment_method')
#         status = request.POST.get('status')

#         print(order_number, transaction_id, payment_method, status)

#         ord = Order.objects.get(user=request.user, order_number=order_number)
#         payment = Payment(
#             user=request.user,
#             transaction_id=transaction_id,
#             payment_method=payment_method,
#             amount=ord.total,
#             status=status,
#         )
#         payment.save()

#         # update the order model
#         ord.payment = payment
#         ord.is_ordered = True
#         ord.save()

#         # move the cart items to ordered food model
#         cart_items = FoodCart.objects.filter(user=request.user)
#         for item in cart_items:
#             o_food = OrderedFood()
#             o_food.order = ord
#             o_food.payment = payment
#             o_food.user = request.user
#             o_food.fooditem = item.fooditem
#             o_food.quantity = item.quantity
#             o_food.price = item.fooditem.price
#             o_food.amount = item.fooditem.price * item.quantity
#             o_food.save()

#         # send order confirmation email to the customer
#         mail_subject = 'Thank you for ordering with us.'
#         mail_template = 'orders/order_confirmation.html'
#         context = {
#             'user': request.user,
#             'ord': ord,
#             'to_email': ord.email,
#         }
#         send_notfication(mail_subject, mail_template, context)

#         # send order recived email to the restaurant
#         mail_subject = 'You have received a new order.'
#         mail_template = 'orders/order_received.html'
#         to_emails = []
#         for i in cart_items:
#             if i.fooditem.restaurant.user.email not in to_emails:
#                 to_emails.append(i.fooditem.restaurant.user.email)
#         print('to_emails ==>', to_emails)
#         context = {
#             'ord': ord,
#             'to_email':  to_emails,
#         }
#         send_notfication(mail_subject, mail_template, context)

#         # clear the cart if payment is scuccess
#         # cart_items.delete()

#         # return back to ajax with status success or failue
#         response = {
#             'order_number': order_number,
#             'transaction_id': transaction_id,
#         }
#         return JsonResponse(response)
#     return HttpResponse('Payments view')
