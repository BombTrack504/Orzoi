from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notfication
# Create your models here.


class Restaurant(models.Model):
    user = models.OneToOneField(
        User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    Restaurant_name = models.CharField(max_length=50)
    restaurant_slug = models.SlugField(max_length=100, unique=True)
    Restaurant_license = models.ImageField(upload_to='Restaurant/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Restaurant_name

    def save(self, *args, **kwargs):
        if self.pk is not None:  # that means, the user is saved in the data based. User exist.
            # update
            orig = Restaurant.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                if self.is_approved == True:
                    # send notification email
                    mail_subject = "congratulations! your restaurant has been approved!"
                    send_notfication(mail_subject, mail_template, context)

                else:
                    mail_subject = "we're sorry! you are not eligible for publishing your restaurant in our marketplace"
                    send_notfication(mail_subject, mail_template, context)
        return super(Restaurant, self).save(*args, **kwargs)
