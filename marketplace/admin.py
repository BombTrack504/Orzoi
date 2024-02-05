from django.contrib import admin

from marketplace.models import FoodCart

# Register your models here.


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'fooditem', 'quantity', 'updated_at')


admin.site.register(FoodCart, CartAdmin)
