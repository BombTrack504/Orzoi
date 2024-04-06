from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.db.models.fields.related import ForeignKey, OneToOneField

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point


# Custom user manager


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("User email must not be null")

        if not username:
            raise ValueError("User name must not be null!!")
        # Create a new user instance with normalized email and provided details
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        # Set password using SHA256 encryption
        user.set_password(password)
        # Save the user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        # Save the superuser to the database
        user.save(using=self._db)
        return user

# Custom User model


class User(AbstractBaseUser):
    RESTAURANT = 1
    CUSTOMER = 2
    ROLE_CHOICE = (
        (RESTAURANT, 'Restaurant'),
        (CUSTOMER, 'Customer'),
    )
    # user fields
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICE, blank=True, null=True)

    # Fields for authentication
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    # Required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # Define the email field as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # Use UserManager for managing user objects
    objects = UserManager()

    def full_name(self):
        return f'{self.first_name}{self.last_name}'

    def __str__(self):
        return self.email  # Return the user's email as the string representation

    # Method to check if user has a specific permission
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Method to check if user has permissions for a specific app module
    def has_module_perms(self, app_label):
        return True

    def get_role(self):
        if self.role == 1:
            user_role = 'Restaurant'
        elif self.role == 2:
            user_role = 'Customer'
        return user_role


class UserProfile(models.Model):
    # One-to-One relationship with User model
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)

    # Fields for user profile information
    profile_picture = models.ImageField(
        upload_to='user/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(
        upload_to='user/cover_pictures', blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=150, blank=True, null=True)
    state = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    location = gismodels.PointField(
        blank=True, null=True, srid=4326)  # Geographical fields
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # def full_address(self):  # con
    #     return f'{self.address_line_1}, {self.address_line_2}'

    def str(self):
        return self.user.email  # Return the email of associated user as string representation

    def save(self, *args, **kwargs):
        # If latitude and longitude are provided, create a Point object for location
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(UserProfile, self).save(*args, **kwargs)
        # Call the save method of the superclass
        return super(UserProfile, self).save(*args, **kwargs)
