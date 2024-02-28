from django.contrib import admin
from Restaurant.models import Restaurant, OpeningHour

# Register your models here.


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('user', 'Restaurant_name', 'is_approved', 'created_at')
    list_display_links = ('user', 'Restaurant_name')
    list_editable = ('is_approved',)


class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'day', 'from_hour', 'to_hour')


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
