from django import forms
from . models import Restaurant, OpeningHour
from accounts.validators import allow_only_images_validator


class RestaurantForm(forms.ModelForm):
    Restaurant_license = forms.FileField(
        label='Restaurant_license',
        widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
        validators=[allow_only_images_validator]
    )

    class Meta:
        model = Restaurant
        fields = ['Restaurant_name', 'Restaurant_license']


class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
