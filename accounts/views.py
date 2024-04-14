from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.conf import settings


from Restaurant.forms import RestaurantForm
from Restaurant.models import Restaurant, ReviewAndRating
from orders.models import Order
from .utils import detectUser, send_verification_email
from . forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.tokens import default_token_generator

from django.core.exceptions import PermissionDenied
# Restrict the Restaurant from accessing the customer
from django.template.defaultfilters import slugify
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django import forms


def check_role_Restaurant(user):  # check restaurant
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restrict the Customer from accessing the Restaurant page


def check_role_Customer(user):  # check customer
    if user.role == 2:
        return True
    else:
        raise PermissionDenied
# Restrict the restaurant from accessing the Customer page


def registerUser(request):
    recaptcha_site_key = settings.RECAPTCHA_PUBLIC_KEY

    # check if user is authemticated or not
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in!')
        # if user already authenticated redirect to respective dashboard
        return redirect('dashboard')

    elif request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            # Extracting clean data from form field
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Create a new user instance
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            # send verification email (utils)
            mail_subject = 'please activate your account'
            email_template = 'accounts/emails/acc_verification_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            messages.success(
                request, 'Your account has been created. Successfully !')
            return redirect('registerUser')
        else:
            messages.error(
                request, 'Invalid form submission. Please check the form errors.')
    else:
        form = UserForm()

    context = {
        'form': form,
        'recaptcha_site_key': recaptcha_site_key,
    }
    return render(request, 'accounts/registerUser.html', context)

    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserForm(request.POST)

        captcha = request.POST.get('g-recaptcha-response')
        captcha_field = ReCaptchaField(
            widget=ReCaptchaV2Checkbox, required=False)

        # check reCAPTCHA
        try:
            captcha_is_valid = captcha_field.clean(captcha)
        except forms.ValidationError:
            captcha_is_valid = False

        if form.is_valid() and captcha_is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            # send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/acc_verification_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            messages.success(
                request, 'Your account has been created successfully!')
            return redirect('registerUser')
        else:
            if not captcha_is_valid:
                messages.error(
                    request, 'reCAPTCHA verification failed. Please try again.')

            messages.error(
                request, 'Registration failed. Please correct the errors below.')

    else:
        form = UserForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerRestaurant(request):
    recaptcha_site_key = settings.RECAPTCHA_PUBLIC_KEY

    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in!')
        return redirect('myAccount')

    elif request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        R_form = RestaurantForm(request.POST, request.FILES)

        if form.is_valid() and R_form.is_valid():
            # Extract user data from UserForm
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Create a new user instance
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            # Extract user data from UserForm
            user.role = User.RESTAURANT
            user.save()
            Restaurant = R_form.save(commit=False)
            Restaurant.user = user
            restaurant_name = R_form.cleaned_data['Restaurant_name']
            # Generate a unique slug for the restaurant
            Restaurant.restaurant_slug = slugify(
                restaurant_name)+'-'+str(user.id)

            user_profile = UserProfile.objects.get(user=user)
            Restaurant.user_profile = user_profile
            Restaurant.save()

            # send verification email
            mail_subject = 'please activate your account'
            email_template = 'accounts/emails/acc_verification_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            messages.success(
                request, 'Your account has been registered successfully! Please wait fot the approval')
            return redirect('registerRestaurant')
        else:
            print('Invalid form or captcha')
            print('invalid form')
            print(form.errors)
            messages.error(
                request, 'Invalid form submission. Please check the form errors.')
    else:
        form = UserForm()
        R_form = RestaurantForm()

    context = {
        'form': form,
        'R_form': R_form,
        'recaptcha_site_key': recaptcha_site_key,
    }
    return render(request, 'accounts/registerRestaurant.html', context)


def activate(request, uidb64, token):
    # activate the user by setting the is_active status to True
    try:
        # Decode the base64-encoded uidb64 to get the user ID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Set the is_active field of the user to True
        user.is_active = True
        user.save()
        messages.success(
            request, 'congratulations!! your acc has been activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')


def login(request):
    # Get the reCAPTCHA site key from settings
    recaptcha_site_key = settings.RECAPTCHA_PUBLIC_KEY
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in!')
        return redirect('myAccount')

    elif request.method == 'POST':
        # If the request method is POST, process the login form data
        # Get email and password from the POST data
        email = request.POST['email']
        password = request.POST['password']
        captcha = request.POST.get('g-recaptcha-response')
        captcha_field = ReCaptchaField(
            widget=ReCaptchaV2Checkbox, required=False)

        # check recaptcha validity
        try:
            captcha_is_valid = captcha_field.clean(captcha)
        except forms.ValidationError:
            captcha_is_valid = False

        if not captcha_is_valid:
            messages.error(
                request, 'reCAPTCHA verification failed. Please try again.')
            return redirect('login')

        # Authenticate user using email and password
        user = auth.authenticate(email=email, password=password)

        if user is not None and captcha_is_valid:
            auth.login(request, user)
            messages.success(request, 'you are now logged in.')
            return redirect('myAccount')

        else:
            messages.error(request, 'invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html', {'recaptcha_site_key': recaptcha_site_key})


def logout(request):
    auth.logout(request)
    messages.info(request, 'your are logged out!')
    return redirect('login')


# decorators
@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirecturl = detectUser(user)
    return redirect(redirecturl)


@login_required(login_url='login')
@user_passes_test(check_role_Customer)  # 403 Forbidden
def Customerdashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent': recent,
    }
    return render(request, 'accounts/Customerdashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def Restaurantdashboard(request):
    restaurant = Restaurant.objects.get(user=request.user)
    orders = Order.objects.filter(
        restaurants__in=[restaurant.id], is_ordered=True).order_by('-created_at')
    recent = orders[:10]

    # total revenue
    total_rev = 0
    for i in orders:
        total_rev += i.get_total_by_res()['grand_total']

    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent': recent,
        'total_rev': total_rev,
    }

    return render(request, 'accounts/Restaurantdashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        # If the request method is POST, extract email from the POST data
        email = request.POST['email']

        if User.objects.filter(email=email).exists():  # check if user exist
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)  # utils

            messages.success(
                request, 'Password rest link has been sent to your email address. Please check youe Gmail')
            return redirect('login')

        else:
            messages.error(
                request, 'Account doesnot exist!')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    # validate the user bt decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Reset your Password")
        return redirect('reset_password')
    else:
        messages.error(request, 'The link to reset your password has expired ')
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successfully!')
            return redirect('login')
        else:
            messages.error(request, 'passowrd do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')


def contact(request):
    return render(request, 'contact.html')


def delete_review(request, review_id):
    review = get_object_or_404(ReviewAndRating, id=review_id)
    if request.user == review.user:  # Ensure only the review author can delete it
        review.delete()
    return redirect('restaurant_detail', restaurant_slug=review.restaurant.restaurant_slug)
