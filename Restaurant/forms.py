from django import forms
from . models import Restaurant
from accounts.validators import allow_only_images_validator


class RestaurantForm(forms.ModelForm):
    Restaurant_license = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn.btn-info'}), validators=[allow_only_images_validator])

    class Meta:
        model = Restaurant
        fields = ['Restaurant_name', 'Restaurant_license']
