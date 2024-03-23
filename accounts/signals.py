from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . models import User, UserProfile

# Signal receiver for post_save event on User model


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    print(created)
    if created:
        # If a new user is created, create a corresponding UserProfile
        UserProfile.objects.create(user=instance)
        print('user profile is created')
    else:
        try:
            # If the user already exists, try to get its UserProfile
            profile = UserProfile.objects.get(user=instance)
            profile.save()  # Save the profile (this line was previously missing parentheses)
        except UserProfile.DoesNotExist:
            # Create a user profile if it does not exist
            UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    pass
