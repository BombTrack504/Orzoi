from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.http import HttpResponse


from Restaurant.forms import RestaurantForm
from .utils import detectUser, send_verification_email
from . forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.tokens import default_token_generator

from django.core.exceptions import PermissionDenied
# Restrict the Restaurant from accessing the customer
from django.template.defaultfilters import slugify


def check_role_Restaurant(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restrict the Customer from accessing the Restaurant page


def check_role_Customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):

    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in!')
        return redirect('dashboard')

    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # User.save()

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
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
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerRestaurant(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in!')
        return redirect('myAccount')

    elif request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        R_form = RestaurantForm(request.POST, request.FILES)

        if form.is_valid() and R_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.RESTAURANT
            user.save()
            Restaurant = R_form.save(commit=False)
            Restaurant.user = user
            restaurant_name = R_form.cleaned_data['Restaurant_name']
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
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        R_form = RestaurantForm()

    context = {
        'form': form,
        'R_form': R_form,
    }
    return render(request, 'accounts/registerRestaurant.html', context)


def activate(request, uidb64, token):
    # activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'congratulations!! your acc has been activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')


def login(request):

    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in!')
        return redirect('myAccount')

    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # check user exist
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'you are now logged in.')
            return redirect('myAccount')

        else:
            messages.error(request, 'invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


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
    return render(request, 'accounts/Customerdashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_Restaurant)  # 403 Forbidden
def Restaurantdashboard(request):
    return render(request, 'accounts/Restaurantdashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
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
