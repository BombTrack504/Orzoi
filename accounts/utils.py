# helper function for features
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from django.conf import settings


def detectUser(user):
    if user.role == 1:
        redirecturl = 'Restaurantdashboard'
        return redirecturl

    elif user.role == 2:
        redirecturl = 'Customerdashboard'
        return redirecturl

    elif user.role == None and user.is_superadmin:
        redirecturl = '/admin'
        return redirecturl


# call from registeruser fun and registerRestaurant fun
def send_verification_email(request, user, mail_subject, email_template):
    # Get the default sender email address
    from_email = settings.DEFAULT_FROM_EMAIL
    # Get the current site domain
    current_site = get_current_site(request)

    # Render the email message template with necessary context data
    message = render_to_string(email_template, {
        'user': user,  # User object
        'domain': current_site,   # Current site domain
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # Encoded user ID
        # Token for verification
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email  # get user email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()


def send_notfication(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    # Render the email message template with the provided context data
    message = render_to_string(mail_template, context)
    # Get the recipient's email address from the context
    if (isinstance(context['to_email'], str)):
        to_email = []
        to_email.append(context['to_email'])
    else:
        to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    mail.send()
