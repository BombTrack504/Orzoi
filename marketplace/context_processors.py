from . models import FoodCart, Tax
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
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = FoodCart.objects.filter(user=request.user)
        for item in cart_items:
            foodItem = FoodItem.objects.get(pk=item.fooditem.id)
            # subtotal = subtotal + (FoodItem.price * item.quantity)
            subtotal += (foodItem.price * item.quantity)

        get_tax = Tax.objects.filter(is_active=True)
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            # Using Nested Dictionary
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        for key in tax_dict.values():
            for x in key.values():
                tax = tax + x

        grandtotal = subtotal + tax
    return dict(subtotal=subtotal, tax=tax, grandtotal=grandtotal, tax_dict=tax_dict)
