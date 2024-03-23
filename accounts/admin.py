from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'username', 'role', 'is_active')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'address', 'country',
                    'state', 'city', 'pin_code', 'latitude', 'longitude',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
