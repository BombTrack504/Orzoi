from django.http import JsonResponse
from django.shortcuts import redirect, render
import requests

from marketplace.models import FoodCart
from marketplace.context_processors import get_cart_amt

from .forms import OrderForm
from .models import Order, OrderedFood, Payment
import simplejson as json
from django.contrib.auth.decorators import login_required
from .utils import create_ord_num
# Create your views here.


@login_required(login_url='login')
def place_order(request):
    cart_items = FoodCart.objects.filter(
        user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

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
            ord.total_tax = json.dumps(total_tax)
            ord.payment_method = request.POST['payment_method']
            ord.save()  # order id (order table pk is generated)
            ord.order_number = create_ord_num(ord.id)
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
    if request.method == 'POST':
        # Retrieve data from the frontend
        data = json.loads(request.body)
        order_number = data.get('order_number')
        amount = data.get('amount')
        token = data.get('token')
        headers = {
            # set this to your desired env variable
            'Authorization': 'Key test_secret_key_28e04cdd720d438d823ee37000feb1cd',
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
            purchases = Order.objects.get(order_number=order_number)

            payment = Payment.objects.create(
                user=request.user,
                payment_method='Khalti',
                amount=amount/100,
                transaction_id=verification_data['idx'],
                # check the response for completed status
                status='Success' if verification_data['state']['name'] == 'Completed' else 'Pending'
            )
            # Update purchase status
            purchases.payment = payment
            purchases.is_ordered = True
            purchases.save()

            # move the cart items to ordered food model
        cart_items = FoodCart.objects.filter(user=request.user)
        print("Number of items in cart:", cart_items.count())
        for item in cart_items:
            purchased_item = OrderedFood()
            purchased_item.order = purchases
            purchased_item.payment = payment
            purchased_item.user = request.user
            purchased_item.fooditem = item.fooditem
            purchased_item.quantity = item.quantity
            purchased_item.price = item.fooditem.price
            purchased_item.amount = item.fooditem.price * item.quantity
            purchased_item.save()

            FoodCart.objects.filter(user=request.user).delete()

            return JsonResponse({'status': 'success'})

        else:
            # Payment failed
            return JsonResponse({'status': 'error', 'message': 'Payment verification failed'})

    else:
        # Handle invalid request method
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
