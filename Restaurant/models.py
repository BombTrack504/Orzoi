from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notfication

from datetime import time
from datetime import date
from datetime import datetime
from django.utils import timezone
from django.db.models import Avg, Count
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

    @property
    def averageReview(self):
        reviews = ReviewAndRating.objects.filter(
            restaurant=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    @property
    def countReview(self):
        reviews = ReviewAndRating.objects.filter(
            restaurant=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def is_open(self):
        # Get today's date in the correct timezone
        today_date = timezone.localdate()

        # Get the current day of the week (1 for Monday, 2 for Tuesday, ..., 7 for Sunday)
        today = today_date.isoweekday()

        # Retrieve opening hours for the current day
        current_opening_hours = OpeningHour.objects.filter(
            restaurant=self, day=today)
        # Get the current time in the correct timezone
        current_time = timezone.localtime().time()

        # Initialize the flag to False
        is_open = False

        # Iterate through the opening hours for the current day
        for opening_hour in current_opening_hours:
            # Check if the restaurant is open during the current time
            if not opening_hour.is_closed:
                start_time = timezone.make_aware(datetime.strptime(
                    opening_hour.from_hour, "%I:%M %p")).time()
                end_time = timezone.make_aware(datetime.strptime(
                    opening_hour.to_hour, "%I:%M %p")).time()

                # Check if the current time is within the opening hours
                if start_time <= current_time < end_time:
                    is_open = True
                    break  # Exit the loop if the restaurant is open

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
                    'to_email': self.user.email
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
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOURS = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p'))
         for h in range(0, 24) for m in range(0, 60, 30)]


class OpeningHour(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS, max_length=20, blank=True)
    to_hour = models.CharField(choices=HOURS, max_length=20, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('restaurant', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        # return self.day
        return self.get_day_display()


class ReviewAndRating(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def str(self):
        return self.subject
