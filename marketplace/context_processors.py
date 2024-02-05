from . models import FoodCart
from menu.models import FoodItem

# Count the total quantity of items in the user's cart


def get_cart_counter(request):
    # Initialize cart_count to zero
    cart_count = 0
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve cart items for the authenticated user
        cart_items = FoodCart.objects.filter(user=request.user)
        # Calculate the total cart count by summing up quantities of each cart item
        cart_count = sum(cart_item.quantity for cart_item in cart_items)
    # Return the total cart count as a dictionary
    return {'cart_count': cart_count}


def get_cart_amt(request):
    subtotal = 0
    tax = 0
    grandtotal = 0

    if request.user.is_authenticated:
        cart_items = FoodCart.objects.filter(user=request.user)
        for item in cart_items:
            foodItem = FoodItem.objects.get(pk=item.fooditem.id)
            # subtotal = subtotal + (FoodItem.price * item.quantity)
            subtotal += (foodItem.price * item.quantity)

        grandtotal = subtotal + tax
    # print(subtotal)
    # print(grand_total)
    return dict(subtotal=subtotal, tax=tax, grandtotal=grandtotal)
