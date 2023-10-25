from django.contrib import admin
from Restaurant.models import Restaurant

# Register your models here.


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('user', 'Restaurant_name', 'is_approved', 'created_at')
    list_display_links = ('user', 'Restaurant_name')
    list_editable = ('is_approved',)


admin.site.register(Restaurant, RestaurantAdmin)
