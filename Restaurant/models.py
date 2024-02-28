from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notfication

from datetime import time
from datetime import date
from datetime import datetime
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

    def is_open(self):
        # check current day opening hour
        today_date = date.today()
        today = today_date.isoweekday()

        current_opening_hour = OpeningHour.objects.filter(
            restaurant=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S")

        is_open = None
        for i in current_opening_hour:
            start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
            end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

            if current_time > start and current_time < end:
                is_open = True
            else:
                is_open = False
        return is_open

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


DAYS = [
    (1, ("Sunday")),
    (2, ("Monday")),
    (3, ("Tuesday")),
    (4, ("Wednesday")),
    (5, ("Thursday")),
    (6, ("Friday")),
    (7, ("Saturday")),
]

HOURS = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p'))
         for h in range(0, 24) for m in range(0, 60, 30)]


class OpeningHour(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOURS, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('restaurant', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        # return self.day
        return self.get_day_display()
